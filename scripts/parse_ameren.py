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
    m = re.search(r"(\d{6})", filename)
    if m:
        return m.group(1)
    return "Unknown"


def main():
    pd.set_option('display.max_columns', None)
    directory = "/Users/hodgesd/Documents/Bill Statements/Ameren"  # Change to your actual PDF directory
    pdf_files = glob.glob(os.path.join(directory, "*2025*.pdf"))
    records = []
    for pdf_path in pdf_files:
        text = extract_text_from_pdf(pdf_path)
        parsed = parse_bill_data(text)
        bill_date = extract_date_from_filename(os.path.basename(pdf_path))
        parsed = {"date": bill_date, **parse_bill_data(text)}
        records.append(parsed)
        print(f"Parsed {pdf_path}: {parsed}")
    df = pd.DataFrame(records)
    print("\nExtracted Data:")
    print(df)

    # Convert date column to datetime format
    try:
        df['date_dt'] = pd.to_datetime(df['date'], format="%Y%m")
    except Exception:
        df['date_dt'] = df['date']

    # Plot as a bar chart
    fig, ax = plt.subplots()
    bars = ax.bar(df['date_dt'], df['net_usage'], color='tab:blue', label='Net Usage')

    # Add total electric bill as labels on top of each bar
    for bar, label in zip(bars, df['electric_bill']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'${label:.2f}',
                ha='center', va='bottom', fontsize=10, color='black')

    # Add labels and title
    ax.set_xlabel("Statement Date")
    ax.set_ylabel("Net Usage (kWh)", color='tab:blue')
    ax.set_title("Net Usage with Total Electric Bill")
    ax.tick_params(axis='y', labelcolor='tab:blue')

    # Rotate x-axis ticks for better readability
    plt.xticks(rotation=45)

    # Show the plot
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
