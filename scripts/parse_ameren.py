# /// script
# dependencies = [
#   "pdfplumber",
#   "pandas",
#   "matplotlib",
# ]
# ///
import glob
import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import pdfplumber  # <-- Replacing PyPDF2 with pdfplumber


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def parse_bill_data(text):
    data = {
        "total_usage": None,
        "total_generation": None,
        "net_usage": None,
        "electric_bill": 0.0,
        "electric_supply": 0.0,
        "electric_delivery": 0.0
    }

    # Improved matching expressions
    total_usage_match = re.search(r"Summary\s+Total kWh\s+(\d{1,5}(?:\.\d+)?)", text)
    if total_usage_match:
        data["total_usage"] = float(total_usage_match.group(1))

    total_generation_match = re.search(r"kWh Out\s+\d+\s+(\d{1,5}(?:\.\d+)?)", text)
    if total_generation_match:
        data["total_generation"] = float(total_generation_match.group(1))

    net_usage_match = re.search(r"Delivery Net Total kWh\s+(-?\d{1,5}(?:\.\d+)?)", text)
    if net_usage_match:
        data["net_usage"] = float(net_usage_match.group(1))

    # Capturing clearly labeled electric charges
    supply_match = re.search(r"Electric Supply[^\$]+\$\s?([\d,.]+)", text)
    delivery_match = re.search(r"Electric Delivery\s*\$(\s?[\d,.]+)", text)
    if supply_match:
        data['electric_supply'] = float(supply_match.group(1).replace(',', ''))

    if delivery_match:
        data['electric_delivery'] = float(delivery_match.group(1).replace(',', ''))

    data["electric_bill"] = data["electric_supply"] + data["electric_delivery"]

    return data


def extract_date_from_filename(filename):
    """Extracts the yyyydd date part from the filename."""
    match = re.search(r'statement-(\d{6})\.pdf', filename)
    if match:
        return match.group(1)  # Return the matched 'yyyydd' part
    raise ValueError(f"Invalid filename format: {filename}")


def main():
    pd.set_option('display.max_columns', None)
    # Specify the directory containing the PDF files
    directory = "/Users/hodgesd/Documents/Bill Statements/Ameren"  # Change to your actual PDF directory

    # Adjust the glob pattern to match the file format 'statement-yyyymm.pdf'
    pdf_files = glob.glob(os.path.join(directory, "statement-*.pdf"))

    records = []
    for pdf_path in pdf_files:
        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_path)

        # Parse the bill data and extract the date
        parsed = parse_bill_data(text)
        bill_date = extract_date_from_filename(os.path.basename(pdf_path))

        # Combine the date with the parsed data
        parsed = {"date": bill_date, **parsed}
        records.append(parsed)
        print(f"Parsed {pdf_path}: {parsed}")

    # Create a DataFrame from the records
    df = pd.DataFrame(records)
    print("\nExtracted Data:")
    print(df)

    # Convert to datetime and sort chronologically
    try:
        df['date_dt'] = pd.to_datetime(df['date'], format="%Y%m")  # Use "%Y%m" for `yyyymm`
    except Exception as e:
        print(f"Date conversion failed: {e}")
        df['date_dt'] = pd.NaT  # Assign NaT for invalid dates

    # Format the date for display as 'yyyy-mm'
    df['formatted_date'] = df['date_dt'].dt.strftime('%Y-%m')

    # Sort by chronological order
    df = df.sort_values(by='date_dt')

    # Debugging: Ensure chronological order
    print("Sorted DataFrame:")
    print(df[['date', 'date_dt', 'formatted_date']])

    # Plot as a bar chart
    fig, ax = plt.subplots()
    bars = ax.bar(df['formatted_date'], df['net_usage'], color='tab:blue', label='Net Usage', width=0.6)

    # Add total electric bill as labels on top (or bottom for negative bars)
    for bar, label in zip(bars, df['electric_bill']):
        height = bar.get_height()
        if height < 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height - 5,  # Position below negative bar
                    f'${label:.2f}', ha='center', va='top', fontsize=10, color='black')
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, height + 5,  # Position above positive bar
                    f'${label:.2f}', ha='center', va='bottom', fontsize=10, color='black')

    # Add a horizontal dotted line at "Net Usage = 0"
    ax.axhline(0, color='gray', linestyle='dotted', linewidth=1)

    # Add labels and title
    ax.set_xlabel("Statement Date")
    ax.set_ylabel("Net Usage (kWh)", color='tab:blue')
    ax.set_title("Net Usage with Total Electric Bill")
    ax.tick_params(axis='x', rotation=45)

    # Ensure the layout fits well
    plt.tight_layout()
    plt.show()
if __name__ == "__main__":
    main()
