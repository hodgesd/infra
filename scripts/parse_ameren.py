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
        "electric_bill": 0.0
    }

    usage_match = re.search(r"Total\s+kWh\s+([-+]?\d+(?:\.\d+)?)", text)
    if usage_match:
        data["total_usage"] = float(usage_match.group(1))

    gen_match = re.search(r"On-Site Excess Gen kWh\s+([-+]?\d+(?:\.\d+)?)", text)
    if gen_match:
        data["total_generation"] = float(gen_match.group(1))

    net_usage_match = re.search(r"Delivery Net Total kWh\s+([-+]?\d+(?:\.\d+)?)", text)
    if net_usage_match:
        data["net_usage"] = float(net_usage_match.group(1))

    # Compute electric bill excluding mandatory fees lines like Customer/Meter Charge
    total_charge = 0.0
    for line in text.splitlines():
        m = re.search(r"\$([-+]?\d+(?:\.\d+)?)", line)
        if m:
            charge_value = float(m.group(1))
            # skip mandatory fees
            if re.search(r"(Customer Charge|Meter Charge)", line, re.IGNORECASE):
                continue
            total_charge += charge_value
    data["electric_bill"] = total_charge

    return data

def extract_date_from_filename(filename):
    m = re.search(r"(20\d{4})", filename)
    if m:
        return m.group(1)
    return "Unknown"

def main():
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

    # Plot
    try:
        df['date_dt'] = pd.to_datetime(df['date'], format="%Y%m")
    except Exception:
        df['date_dt'] = df['date']

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Statement Date")
    ax1.set_ylabel("Net Usage (kWh)", color='tab:blue')
    ax1.plot(df['date_dt'], df['net_usage'], marker='o', linestyle='-', color='tab:blue', label='Net Usage')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Electric Bill ($)', color='tab:red')
    ax2.plot(df['date_dt'], df['electric_bill'], marker='s', linestyle='--', color='tab:red', label="Electric Bill")
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title("Net Usage and Electric Bill Over Time")
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
