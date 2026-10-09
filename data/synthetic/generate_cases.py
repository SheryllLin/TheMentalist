"""
Synthetic Investigation Dataset Generator
==========================================
Generates 4 fictional investigation cases with realistic but entirely fabricated data.
ALL names, phone numbers, account numbers, and locations are invented for demonstration.
Nothing in this dataset represents real individuals or events.

Run: python data/synthetic/generate_cases.py
Output: data/synthetic/cases/*.txt  and  data/synthetic/cases/*.json  and *.csv
"""
import json
import os
import random
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "cases")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def rand_date(start: datetime, days_range: int) -> str:
    return (start + timedelta(days=random.randint(0, days_range),
                              hours=random.randint(0, 23),
                              minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M")


def rand_phone() -> str:
    return f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"


def rand_account() -> str:
    return f"ACCT-{random.randint(1000000000, 9999999999)}"


# =========================================================
# CASE 1: Organized Financial Fraud Network
# =========================================================
def generate_case1():
    start = datetime(2026, 1, 10)
    text = """
CASE FILE: CASE-2026-ALPHA
TYPE: Organized Financial Fraud
CLASSIFICATION: SYNTHETIC DEMONSTRATION DATA

INCIDENT SUMMARY
On 10 January 2026, the Financial Intelligence Unit flagged a series of suspicious
transactions routed through shell companies. Investigation revealed an organized network
operating out of Mumbai, Pune, and Hyderabad.

PERSONS OF INTEREST

1. Arjun Mehta (alias: A.M., Arjun M.)
   Phone: +91-98201-55431
   Email: arjun.mehta.pvt@fastmail.com
   Known associate of Priya Verma and Siddharth Rao.
   Believed to be the financial coordinator of the scheme.

2. Priya Verma (alias: P. Verma)
   Phone: +91-80034-22190
   Director of Goldline Exports Pvt. Ltd. (front company).
   Frequently visited Delhi and Pune.

3. Siddharth Rao
   Phone: +91-77711-88223
   Manages mule accounts linked to Arjun Mehta.
   Traveled to Dubai on 15 January 2026 and 2 February 2026.

4. Ritu Shah
   Phone: +91-90005-33411
   Bank employee suspected of facilitating fraudulent KYC approvals.

ORGANIZATIONS

- Goldline Exports Pvt. Ltd.
  Registered: Mumbai. Director: Priya Verma.
  Account: ACCT-4837291045

- Nexus Traders LLP
  Registered: Hyderabad. Linked to Siddharth Rao.
  Account: ACCT-7712904833

- FastCash Finance
  Unofficial money transfer service used for layering.

TIMELINE OF EVENTS

10 Jan 2026 — Arjun Mehta met Priya Verma at Hotel Grand, Mumbai.
12 Jan 2026 — Goldline Exports received INR 45,00,000 from an unidentified foreign account.
14 Jan 2026 — Priya Verma transferred INR 18,00,000 to Nexus Traders LLP.
15 Jan 2026 — Siddharth Rao departed Mumbai for Dubai. Phone activity ceased.
18 Jan 2026 — Ritu Shah approved three new accounts at Bangalore Branch. All linked to Nexus Traders.
20 Jan 2026 — Arjun Mehta called Ritu Shah (duration: 14 minutes).
22 Jan 2026 — INR 12,00,000 transferred from Nexus Traders to a personal account held by Arjun Mehta.
28 Jan 2026 — Siddharth Rao returned from Dubai. Met Arjun Mehta at Cafe Lattitude, Pune.
2 Feb 2026  — Second Dubai trip by Siddharth Rao.
5 Feb 2026  — Goldline Exports dissolved. Assets moved to FastCash Finance.

COMMUNICATIONS

+91-98201-55431 called +91-80034-22190 on 09 Jan 2026 at 14:32 (duration 8 min)
+91-98201-55431 called +91-77711-88223 on 10 Jan 2026 at 09:14 (duration 22 min)
+91-80034-22190 called +91-90005-33411 on 17 Jan 2026 at 11:05 (duration 6 min)
+91-77711-88223 called +91-98201-55431 on 27 Jan 2026 at 20:44 (duration 11 min)

FINANCIAL TRANSACTIONS (SUMMARY)
See attached file: case1_transactions.csv
"""
    with open(os.path.join(OUTPUT_DIR, "case1_financial_fraud.txt"), "w") as f:
        f.write(text.strip())

    # Structured transaction CSV
    transactions = [
        {"tx_id": "TX-001", "sender_account": "ACCT-FOREIGN-001", "receiver_account": "ACCT-4837291045",
         "amount": 4500000, "currency": "INR", "timestamp": "2026-01-12 10:30", "transaction_type": "CREDIT",
         "description": "Payment for export invoice INV-2026-01"},
        {"tx_id": "TX-002", "sender_account": "ACCT-4837291045", "receiver_account": "ACCT-7712904833",
         "amount": 1800000, "currency": "INR", "timestamp": "2026-01-14 15:22", "transaction_type": "TRANSFER",
         "description": "Inter-company transfer"},
        {"tx_id": "TX-003", "sender_account": "ACCT-7712904833", "receiver_account": "ACCT-9001234567",
         "amount": 1200000, "currency": "INR", "timestamp": "2026-01-22 11:00", "transaction_type": "TRANSFER",
         "description": "Consultant fees - A. Mehta"},
        {"tx_id": "TX-004", "sender_account": "ACCT-FOREIGN-001", "receiver_account": "ACCT-4837291045",
         "amount": 3200000, "currency": "INR", "timestamp": "2026-01-30 09:15", "transaction_type": "CREDIT",
         "description": "Second export payment"},
        {"tx_id": "TX-005", "sender_account": "ACCT-4837291045", "receiver_account": "ACCT-FASTCASH-01",
         "amount": 5000000, "currency": "INR", "timestamp": "2026-02-05 16:00", "transaction_type": "TRANSFER",
         "description": "Asset liquidation"},
    ]
    import csv
    with open(os.path.join(OUTPUT_DIR, "case1_transactions.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)

    print("Generated: case1_financial_fraud.txt + case1_transactions.csv")


# =========================================================
# CASE 2: Vehicle Theft Network
# =========================================================
def generate_case2():
    text = """
CASE FILE: CASE-2026-BETA
TYPE: Organized Vehicle Theft Network
CLASSIFICATION: SYNTHETIC DEMONSTRATION DATA

INCIDENT SUMMARY
Between November 2025 and February 2026, seventeen high-value vehicles were reported stolen
across Delhi NCR. A surveillance operation identified a coordinated chop-shop network operating
in Faridabad and Gurgaon.

PERSONS OF INTEREST

1. Karim Ansari (alias: K.A., Karim bhai)
   Phone: +91-85551-99012
   Believed to be the network coordinator.
   Operates from Faridabad Industrial Area.

2. Deepak Nair
   Phone: +91-94433-70822
   Driver and lookout. Linked to at least 6 theft incidents.
   Drives a Silver Honda City (DL 8C 1122 — reported stolen Feb 2026).

3. Sunita Malhotra
   Phone: +91-73322-55601
   Suspected of facilitating forged documents for re-registration.
   Works at a regional transport office (identity protected in this document).

4. Ravi Kulkarni
   Phone: +91-88870-44212
   Chop shop operator, Gurgaon. Linked to Karim Ansari.

ORGANIZATIONS

- K.A. Auto Parts
  Unregistered business, Faridabad Industrial Area.
  Receives stolen vehicle components.

- SwiftDoc Services
  Forged documentation service linked to Sunita Malhotra.

VEHICLES (STOLEN)

VH-001: Toyota Fortuner | DL 3C 4455 | Stolen: 2025-11-15 | Recovered: No
VH-002: Mercedes-Benz GLE | DL 2B 9901 | Stolen: 2025-12-02 | Recovered: Partial
VH-003: Honda CR-V | HR 26 8872 | Stolen: 2026-01-08 | Recovered: No

TIMELINE OF EVENTS

15 Nov 2025 — Toyota Fortuner stolen from Sector 18 parking, Noida.
16 Nov 2025 — Karim Ansari contacted Ravi Kulkarni (call 18 min).
02 Dec 2025 — Mercedes GLE stolen. Deepak Nair's phone pinged near scene.
10 Dec 2025 — Deepak Nair met Karim Ansari at Dhaba 44, Faridabad.
08 Jan 2026 — Honda CR-V stolen, Dwarka. Deepak Nair's vehicle sighted nearby.
15 Jan 2026 — Sunita Malhotra received payment of INR 85,000 from K.A. Auto Parts.
20 Jan 2026 — Re-registration documents for DL 3C 4455 filed under false identity.
28 Jan 2026 — Ravi Kulkarni arrested at Gurgaon workshop. Three vehicles found dismantled.

COMMUNICATIONS

+91-85551-99012 called +91-94433-70822 on 15 Nov 2025 at 23:10 (duration 4 min)
+91-85551-99012 called +91-88870-44212 on 16 Nov 2025 at 07:22 (duration 18 min)
+91-94433-70822 called +91-85551-99012 on 02 Dec 2025 at 01:15 (duration 2 min)
+91-73322-55601 called +91-85551-99012 on 12 Jan 2026 at 14:30 (duration 9 min)
"""
    with open(os.path.join(OUTPUT_DIR, "case2_vehicle_theft.txt"), "w") as f:
        f.write(text.strip())
    print("Generated: case2_vehicle_theft.txt")


# =========================================================
# CASE 3: Kidnapping Investigation
# =========================================================
def generate_case3():
    text = """
CASE FILE: CASE-2026-GAMMA
TYPE: Kidnapping for Ransom
CLASSIFICATION: SYNTHETIC DEMONSTRATION DATA

INCIDENT SUMMARY
On 5 March 2026, Vikram Bose (age 42, businessman) was abducted from outside his
residence in Koramangala, Bangalore. A ransom demand of INR 2 crore was received
the following day.

PERSONS OF INTEREST

1. Harish Pillai (alias: Harry, H.P.)
   Phone: +91-99880-77654
   Primary suspect. Former employee of Bose Industries.
   Dismissed in December 2025 following financial dispute.

2. Leela Nair
   Phone: +91-82200-33991
   Believed to have assisted with logistics. Relationship to Harish unknown.

3. Mangesh Tiwari
   Phone: +91-76655-44230
   Driver of abduction vehicle (White Innova, MH 12 JJ 8891).
   Last seen in Mysuru on 7 March 2026.

VICTIM

- Vikram Bose
  DOB: 1984-07-14
  Address: 14B Koramangala 5th Block, Bangalore.
  Director, Bose Industries Pvt. Ltd.

TIMELINE OF EVENTS

01 Mar 2026 — Harish Pillai contacted Vikram Bose's office requesting meeting. Denied.
03 Mar 2026 — Harish Pillai observed surveilling Vikram Bose's residence (CCTV footage).
05 Mar 2026 — Vikram Bose abducted at 07:45. Witnesses report white Innova.
06 Mar 2026 — Anonymous call received by Bose family. Ransom: INR 2 crore. 48-hour deadline.
06 Mar 2026 — Cell tower data places +91-99880-77654 near Tumkur Road.
07 Mar 2026 — Mangesh Tiwari's vehicle spotted on NH-275 near Mysuru (ANPR camera).
08 Mar 2026 — Partial ransom payment of INR 40,00,000 transferred to account ACCT-1199003344.
09 Mar 2026 — Vikram Bose found alive near Channapatna. Minor injuries.
10 Mar 2026 — Harish Pillai arrested, Mysuru. Mangesh Tiwari still at large.

COMMUNICATIONS

+91-99880-77654 called +91-82200-33991 on 03 Mar 2026 at 22:55 (duration 31 min)
+91-99880-77654 called +91-76655-44230 on 04 Mar 2026 at 06:10 (duration 5 min)
BLOCKED NUMBER called Bose family landline on 06 Mar 2026 at 11:02 (duration 2 min)
+91-82200-33991 called +91-76655-44230 on 07 Mar 2026 at 14:00 (duration 7 min)

FINANCIAL

- ACCT-1199003344 (Unknown holder) received INR 40,00,000 on 08 Mar 2026.
- Account opened 1 March 2026. Operated for 3 days. Funds withdrawn via ATM Mysuru.
"""
    with open(os.path.join(OUTPUT_DIR, "case3_kidnapping.txt"), "w") as f:
        f.write(text.strip())
    print("Generated: case3_kidnapping.txt")


# =========================================================
# CASE 4: Cyber-Enabled Fraud
# =========================================================
def generate_case4():
    text = """
CASE FILE: CASE-2026-DELTA
TYPE: Cyber-Enabled Investment Fraud
CLASSIFICATION: SYNTHETIC DEMONSTRATION DATA

INCIDENT SUMMARY
Between October 2025 and January 2026, 340 victims across India were defrauded of
approximately INR 8.5 crore through a fake cryptocurrency investment platform
called "CryptoMax India." The platform was operated via Telegram groups and fake websites.

PERSONS OF INTEREST

1. Nitesh Joshi
   Phone: +91-91234-00981
   Email: nitesh.joshi.tech@protonmail.com
   Suspected operator of CryptoMax India platform.
   Telegram: @crypto_nitesh

2. Ananya Sharma
   Phone: +91-80012-44900
   Social media recruitment for investment scheme.
   Instagram: @ananya_grows_wealth

3. Pavel Novak (foreign national)
   Suspected to have provided technical infrastructure.
   IP addresses traced to Eastern Europe.

4. Rakesh Gupta
   Phone: +91-96680-22113
   Local payment aggregator. Operated mule accounts for fund collection.

ORGANIZATIONS

- CryptoMax India (fake entity)
  Website: cryptomaxindia[.]com (domain now suspended)
  Telegram group: 4,200 members at peak

- FastPay Solutions
  Payment service used for initial fund collection. Linked to Rakesh Gupta.

MODUS OPERANDI

1. Victims approached via Telegram and Instagram with promises of 30-40% monthly returns.
2. Victims asked to invest minimum INR 5,000. Early investors paid artificial returns.
3. Large investors (above INR 1,00,000) invited to "premium" Telegram channel.
4. In January 2026, platform withdrew all funds and went offline.

FINANCIAL SUMMARY (AGGREGATED)

Total collected: INR 8,50,00,000
Total victims: 340
Average loss per victim: INR 25,000
Largest single loss: INR 15,00,000 (victim identity protected)
Funds routed through: FastPay Solutions → ACCT-5544332211 → ACCT-9988776655 → Crypto exchange

TIMELINE

Oct 2025      — CryptoMax India Telegram group created by @crypto_nitesh.
Nov 2025      — Ananya Sharma begins promoting scheme on Instagram.
Dec 2025      — 200+ victims have invested. Platform shows fabricated profits.
15 Jan 2026   — Rakesh Gupta transfers INR 3.2 crore offshore via crypto exchange.
20 Jan 2026   — Platform goes offline. Telegram group deleted.
22 Jan 2026   — First FIRs filed. Cyber Cell investigation begins.
28 Jan 2026   — Ananya Sharma arrested, Chennai.

DIGITAL EVIDENCE

- IP logs: 185.220.101.x (Tor exit node) accessed admin panel.
- Domain cryptomaxindia[.]com registered via privacy-protected registrar.
- Telegram account @crypto_nitesh linked to SIM registered to false identity.
- FastPay Solutions KYC documents fraudulent (confirmed).
"""
    with open(os.path.join(OUTPUT_DIR, "case4_cyber_fraud.txt"), "w") as f:
        f.write(text.strip())

    # CDR data for case 4
    cdr = [
        {"caller": "+91-91234-00981", "receiver": "+91-80012-44900", "timestamp": "2025-10-05 10:22",
         "duration_sec": 420, "cell_tower": "TOWER-MUM-0012"},
        {"caller": "+91-91234-00981", "receiver": "+91-96680-22113", "timestamp": "2025-11-15 14:10",
         "duration_sec": 750, "cell_tower": "TOWER-MUM-0077"},
        {"caller": "+91-80012-44900", "receiver": "+91-91234-00981", "timestamp": "2025-12-01 09:33",
         "duration_sec": 180, "cell_tower": "TOWER-CHE-0033"},
        {"caller": "+91-96680-22113", "receiver": "+91-91234-00981", "timestamp": "2026-01-14 20:05",
         "duration_sec": 900, "cell_tower": "TOWER-DEL-0221"},
        {"caller": "+91-96680-22113", "receiver": "+91-80012-44900", "timestamp": "2026-01-16 08:45",
         "duration_sec": 300, "cell_tower": "TOWER-DEL-0221"},
    ]
    import csv
    with open(os.path.join(OUTPUT_DIR, "case4_cdr.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cdr[0].keys())
        writer.writeheader()
        writer.writerows(cdr)

    print("Generated: case4_cyber_fraud.txt + case4_cdr.csv")


# =========================================================
# CASE metadata manifest
# =========================================================
def generate_manifest():
    manifest = [
        {
            "case_number": "CASE-2026-001",
            "title": "Organized Financial Fraud Network",
            "description": "Multi-city financial fraud involving shell companies, money mules, and hawala transfers.",
            "priority": "HIGH",
            "files": ["case1_financial_fraud.txt", "case1_transactions.csv"]
        },
        {
            "case_number": "CASE-2026-002",
            "title": "Vehicle Theft Ring — Delhi NCR",
            "description": "Coordinated vehicle theft network with chop shops across Faridabad and Gurgaon.",
            "priority": "MEDIUM",
            "files": ["case2_vehicle_theft.txt"]
        },
        {
            "case_number": "CASE-2026-003",
            "title": "Kidnapping for Ransom — Bangalore",
            "description": "Abduction of a businessman; ransom demand; partial payment traced.",
            "priority": "CRITICAL",
            "files": ["case3_kidnapping.txt"]
        },
        {
            "case_number": "CASE-2026-004",
            "title": "CryptoMax Investment Fraud",
            "description": "Cyber-enabled investment fraud affecting 340+ victims nationwide via fake crypto platform.",
            "priority": "HIGH",
            "files": ["case4_cyber_fraud.txt", "case4_cdr.csv"]
        },
    ]
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("Generated: manifest.json")


if __name__ == "__main__":
    print("Generating synthetic investigation dataset...")
    print("NOTE: All data is entirely fictional for demonstration purposes.\n")
    generate_case1()
    generate_case2()
    generate_case3()
    generate_case4()
    generate_manifest()
    print("\nDone. Files written to:", OUTPUT_DIR)
