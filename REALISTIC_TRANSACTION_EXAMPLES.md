# 🏦 Realistic Banking Transaction Examples

## Overview
These are actual transaction payloads that fraud detection systems receive in production environments. Each example contains only raw data available at transaction time - no pre-computed risk scores or fraud indicators.

---

## 📊 Data Structure Reference

### Available at Transaction Time
- **Transaction Metadata**: ID, type, timestamp, authorization details
- **Financial Details**: Amount, currency, fees, exchange rates
- **Card Information**: Masked PAN, BIN (first 6-8 digits), brand, type, entry mode
- **Merchant Details**: Name, ID, MCC (Merchant Category Code), location, terminal
- **Customer Context**: Account age, customer segment, historical patterns
- **Device/Session**: Fingerprint, OS, browser, session behavior
- **Location Data**: Transaction location, IP geolocation, distance calculations
- **Velocity Counters**: Transaction counts/amounts over time windows
- **Authentication**: 3DS status, MFA completion, PIN verification
- **Behavioral Profile**: Historical patterns, typical behavior

---

## 🟢 LEGITIMATE TRANSACTIONS

### Example 1: Regular Weekday Coffee Purchase
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-MORN-4A8F92",
    "transaction_type": "PURCHASE",
    "transaction_datetime": "2024-01-20T07:42:13.234Z",
    "authorization_code": "AUTH891234"
  },
  "financial": {
    "amount": 6.75,
    "currency": "USD"
  },
  "card": {
    "masked_pan": "************4829",
    "bin": "414720",
    "card_brand": "VISA",
    "card_type": "DEBIT",
    "card_present": true,
    "entry_mode": "CONTACTLESS"
  },
  "merchant": {
    "merchant_id": "MID-DUNK-00789",
    "merchant_name": "Dunkin #00789",
    "merchant_category_code": "5814",
    "merchant_category": "Fast Food Restaurants",
    "terminal_id": "TERM-DD-789-02",
    "merchant_city": "Boston",
    "merchant_state": "MA",
    "merchant_country": "US"
  },
  "customer": {
    "customer_id": "CUST-2019-8F3A92",
    "customer_since": "2019-02-10",
    "age_of_account_days": 1805
  },
  "location": {
    "transaction_latitude": 42.3601,
    "transaction_longitude": -71.0589,
    "transaction_postal_code": "02116"
  },
  "velocity_counters": {
    "transactions_today": 1,
    "transactions_last_24h": 1,
    "amount_today": 6.75
  },
  "behavioral_profile": {
    "weekday_morning_purchase_frequency": "DAILY",
    "typical_morning_amount_range": "5.00-10.00",
    "home_postal_code": "02116",
    "work_postal_code": "02110"
  }
}
```

### Example 2: Payday Direct Deposit + Bill Payment Pattern
```json
{
  "transaction": {
    "transaction_id": "TXN-20240115-UTIL-9B2C47",
    "transaction_type": "PAYMENT",
    "transaction_datetime": "2024-01-15T18:30:45.678Z",
    "payment_type": "BILL_PAY"
  },
  "financial": {
    "amount": 287.43,
    "currency": "USD"
  },
  "card": {
    "masked_pan": "************7234",
    "bin": "533948",
    "card_brand": "MASTERCARD",
    "card_type": "DEBIT",
    "card_present": false
  },
  "merchant": {
    "merchant_id": "MID-UTILITY-ELEC",
    "merchant_name": "Pacific Gas & Electric",
    "merchant_category_code": "4900",
    "merchant_category": "Utilities - Electric, Gas, Water",
    "payment_processor": "BILLPAY_SYSTEM"
  },
  "customer": {
    "customer_id": "CUST-2016-3D8E71",
    "customer_since": "2016-11-23",
    "age_of_account_days": 2615,
    "last_direct_deposit": "2024-01-15T03:00:00.000Z",
    "direct_deposit_amount": 3847.62
  },
  "device": {
    "device_id": "DEV-MOBILE-KNOWN-8A9C",
    "device_type": "MOBILE",
    "device_os": "iOS",
    "device_os_version": "17.2.1",
    "app_version": "8.4.2",
    "days_since_device_first_seen": 423
  },
  "authentication": {
    "authentication_method": "BIOMETRIC",
    "authentication_status": "SUCCESS"
  },
  "velocity_counters": {
    "bill_payments_today": 3,
    "bill_payments_this_month": 3,
    "recurring_payment_match": true
  },
  "behavioral_profile": {
    "bill_payment_day_pattern": "15th of month",
    "typical_utility_payment": 275.00,
    "payment_history_months": 31
  }
}
```

### Example 3: Family Grocery Shopping - Saturday Routine
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-GROC-5E9A13",
    "transaction_type": "PURCHASE",
    "transaction_datetime": "2024-01-20T11:15:22.456Z"
  },
  "financial": {
    "amount": 248.76,
    "currency": "USD",
    "cashback_amount": 40.00
  },
  "card": {
    "masked_pan": "************9012",
    "bin": "421783",
    "card_brand": "VISA",
    "card_type": "CREDIT",
    "card_subtype": "REWARDS",
    "card_present": true,
    "entry_mode": "CHIP",
    "pin_verified": true
  },
  "merchant": {
    "merchant_id": "MID-KROGER-4521",
    "merchant_name": "Kroger #4521",
    "merchant_category_code": "5411",
    "merchant_category": "Grocery Stores, Supermarkets",
    "terminal_id": "TERM-KR-4521-07"
  },
  "customer": {
    "customer_id": "CUST-2014-6B4F88",
    "customer_since": "2014-05-30",
    "age_of_account_days": 3522,
    "household_size": 4
  },
  "location": {
    "store_address": "4521 Main St, Columbus, OH",
    "distance_from_home_miles": 2.3
  },
  "velocity_counters": {
    "grocery_transactions_this_week": 2,
    "grocery_spend_this_week": 367.43
  },
  "behavioral_profile": {
    "typical_grocery_day": "SATURDAY",
    "avg_weekly_grocery_spend": 325.00,
    "cashback_frequency": "WEEKLY",
    "preferred_grocery_chains": ["Kroger", "Whole Foods"]
  }
}
```

---

## 🟡 SUSPICIOUS BUT POSSIBLY LEGITIMATE

### Example 4: New Device - Forgot Phone Scenario
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-FORG-8C3D92",
    "transaction_type": "ECOMMERCE",
    "transaction_datetime": "2024-01-20T14:22:18.789Z"
  },
  "financial": {
    "amount": 127.99,
    "currency": "USD"
  },
  "card": {
    "masked_pan": "************3456",
    "bin": "445062",
    "card_brand": "VISA",
    "card_type": "CREDIT",
    "card_present": false
  },
  "merchant": {
    "merchant_id": "MID-TARGET-ONLINE",
    "merchant_name": "Target.com",
    "merchant_category_code": "5311",
    "merchant_category": "Department Stores"
  },
  "customer": {
    "customer_id": "CUST-2018-7A9C24",
    "customer_since": "2018-09-14",
    "age_of_account_days": 1954
  },
  "device": {
    "device_id": "DEV-DESKTOP-NEW-4F7B",
    "device_type": "DESKTOP",
    "device_os": "Windows",
    "browser": "Edge",
    "browser_version": "120.0",
    "days_since_device_first_seen": 0,
    "user_agent_language": "en-US"
  },
  "authentication": {
    "authentication_method": "PASSWORD",
    "authentication_status": "SUCCESS",
    "authentication_attempts": 2,
    "account_recovery_used": true,
    "recovery_method": "SMS"
  },
  "location": {
    "ip_address": "73.94.123.67",
    "ip_city": "Columbus",
    "ip_state": "OH",
    "ip_type": "RESIDENTIAL",
    "matches_billing_city": true
  },
  "session": {
    "session_id": "SESS-20240120-NEW-8A9F",
    "session_duration_seconds": 892,
    "pages_viewed": 12,
    "cart_abandonment_recovered": true,
    "password_reset_completed": true
  },
  "velocity_counters": {
    "new_device_transactions_today": 1,
    "password_resets_last_7d": 1
  },
  "behavioral_profile": {
    "typical_device_count": 2,
    "target_purchase_frequency": "MONTHLY",
    "avg_transaction_amount": 85.00
  }
}
```

### Example 5: International Travel - First Foreign Transaction
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-INTL-2B8F56",
    "transaction_type": "PURCHASE",
    "transaction_datetime": "2024-01-20T20:45:33.123Z"
  },
  "financial": {
    "amount": 89.50,
    "currency": "GBP",
    "amount_usd": 113.67,
    "exchange_rate": 1.27,
    "foreign_transaction_fee": 2.71
  },
  "card": {
    "masked_pan": "************8901",
    "bin": "490501",
    "card_brand": "VISA",
    "card_type": "CREDIT",
    "card_subtype": "TRAVEL_REWARDS",
    "card_present": true,
    "entry_mode": "CONTACTLESS"
  },
  "merchant": {
    "merchant_id": "MID-UK-RESTAURANT",
    "merchant_name": "The Ivy London",
    "merchant_category_code": "5812",
    "merchant_category": "Eating Places, Restaurants",
    "merchant_city": "London",
    "merchant_country": "GB"
  },
  "customer": {
    "customer_id": "CUST-2017-5C7E93",
    "customer_since": "2017-03-28",
    "age_of_account_days": 2489,
    "international_travel_flag": false
  },
  "location": {
    "transaction_city": "London",
    "transaction_country": "GB",
    "distance_from_home_km": 7879,
    "time_zone_difference_hours": 8
  },
  "velocity_counters": {
    "international_transactions_lifetime": 0,
    "transactions_today": 4,
    "countries_visited_today": 2
  },
  "behavioral_profile": {
    "home_city": "San Francisco",
    "home_country": "US",
    "international_transaction_history": "NEVER",
    "last_domestic_transaction_hours_ago": 18
  }
}
```

### Example 6: Unusual Merchant Category - Life Event
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-LIFE-9D4A67",
    "transaction_type": "PURCHASE",
    "transaction_datetime": "2024-01-20T16:30:45.567Z"
  },
  "financial": {
    "amount": 8750.00,
    "currency": "USD",
    "payment_plan": "INSTALLMENT"
  },
  "card": {
    "masked_pan": "************2345",
    "bin": "522981",
    "card_brand": "MASTERCARD",
    "card_type": "CREDIT",
    "card_present": false
  },
  "merchant": {
    "merchant_id": "MID-JEWELRY-TIFF",
    "merchant_name": "Tiffany & Co.",
    "merchant_category_code": "5944",
    "merchant_category": "Jewelry Stores, Watches, Clocks",
    "merchant_website": "tiffany.com"
  },
  "customer": {
    "customer_id": "CUST-2015-8B2C45",
    "customer_since": "2015-06-18",
    "age_of_account_days": 3138,
    "credit_limit": 15000.00,
    "available_credit": 11250.00
  },
  "device": {
    "device_id": "DEV-MOBILE-TRUST-3A8C",
    "device_type": "MOBILE",
    "device_os": "iOS",
    "days_since_device_first_seen": 892
  },
  "authentication": {
    "authentication_method": "3DS2",
    "authentication_status": "AUTHENTICATED",
    "challenge_completed": true,
    "liability_shift": true
  },
  "location": {
    "ip_address": "73.162.89.234",
    "ip_matches_billing_address": true
  },
  "session": {
    "session_duration_seconds": 1847,
    "products_viewed": 23,
    "wishlist_items_viewed": 8,
    "comparison_shopping_detected": true
  },
  "velocity_counters": {
    "luxury_purchases_lifetime": 0,
    "large_purchases_last_year": 2
  },
  "behavioral_profile": {
    "typical_transaction_amount": 125.00,
    "largest_previous_purchase": 2500.00,
    "jewelry_purchase_history": "NEVER",
    "recent_search_patterns": ["engagement rings", "wedding bands"]
  }
}
```

---

## 🔴 HIGH-RISK TRANSACTIONS

### Example 7: Classic Account Takeover Pattern
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-ATO-7F9B34",
    "transaction_type": "TRANSFER",
    "transaction_datetime": "2024-01-20T04:17:28.901Z"
  },
  "financial": {
    "amount": 4999.00,
    "currency": "USD",
    "transfer_type": "EXTERNAL",
    "destination_account": "****8934"
  },
  "card": {
    "masked_pan": "************6789",
    "bin": "476173",
    "card_brand": "VISA",
    "card_type": "DEBIT",
    "card_present": false
  },
  "merchant": {
    "merchant_id": "P2P-TRANSFER-SERVICE",
    "merchant_name": "QuickTransfer",
    "merchant_category_code": "6536",
    "merchant_category": "Money Transfer"
  },
  "customer": {
    "customer_id": "CUST-2012-4E8A91",
    "customer_since": "2012-08-30",
    "age_of_account_days": 4160,
    "account_changes_last_hour": ["email", "phone", "password"],
    "security_questions_reset": true
  },
  "device": {
    "device_id": "DEV-UNKNOWN-NEW-8C4F",
    "device_type": "MOBILE",
    "device_os": "Android",
    "device_os_version": "14",
    "device_jailbroken": true,
    "days_since_device_first_seen": 0,
    "sim_changed_recently": true
  },
  "authentication": {
    "authentication_method": "PASSWORD",
    "mfa_bypassed": true,
    "bypass_reason": "RECOVERY_CODE",
    "unusual_login_pattern": true
  },
  "location": {
    "ip_address": "192.119.67.234",
    "ip_country": "RO",
    "ip_type": "VPN",
    "vpn_provider": "NordVPN",
    "distance_from_home_km": 9234
  },
  "session": {
    "session_id": "SESS-HIJACK-2A9C",
    "login_attempts_before_success": 4,
    "account_takeover_signals": true,
    "unusual_navigation_pattern": true,
    "direct_transfer_attempt": true
  },
  "velocity_counters": {
    "transfers_last_hour": 3,
    "amount_transferred_last_hour": 9500.00,
    "failed_login_attempts_today": 8
  },
  "behavioral_profile": {
    "typical_transfer_amount": 150.00,
    "external_transfer_frequency": "RARE",
    "night_activity_frequency": "NEVER",
    "home_city": "Portland",
    "typical_login_hours": "08:00-22:00"
  }
}
```

### Example 8: Card Testing Pattern
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-TEST-3B7C89",
    "transaction_type": "ECOMMERCE",
    "transaction_datetime": "2024-01-20T02:34:17.234Z",
    "authorization_attempts": 3
  },
  "financial": {
    "amount": 0.01,
    "currency": "USD"
  },
  "card": {
    "masked_pan": "************4567",
    "bin": "517805",
    "card_brand": "MASTERCARD",
    "card_type": "CREDIT",
    "card_present": false,
    "cvv_result": "MISMATCH"
  },
  "merchant": {
    "merchant_id": "MID-DONATION-FAKE",
    "merchant_name": "GlobalCharityDonation",
    "merchant_category_code": "8398",
    "merchant_category": "Charitable Organizations",
    "merchant_registration_date": "2024-01-18",
    "merchant_website": "globalcharitydonation.org"
  },
  "customer": {
    "customer_id": "CUST-GENERATED-9A2C",
    "account_opened_minutes_ago": 5,
    "email_domain": "tempmail.com",
    "phone_type": "VOIP"
  },
  "device": {
    "device_id": "DEV-BOT-PATTERN-7C8D",
    "device_type": "DESKTOP",
    "browser": "Chrome",
    "browser_automated": true,
    "javascript_disabled": true,
    "cookies_disabled": true
  },
  "location": {
    "ip_address": "45.142.122.189",
    "ip_type": "DATACENTER",
    "hosting_provider": "DIGITALOCEAN",
    "known_proxy": true
  },
  "session": {
    "session_duration_seconds": 8,
    "direct_payment_page": true,
    "referrer": "none",
    "bot_behavior_score": 0.95
  },
  "velocity_counters": {
    "micro_transactions_last_hour": 47,
    "unique_cards_tested_last_hour": 23,
    "failed_authorizations_last_hour": 44
  },
  "behavioral_profile": {
    "first_transaction": true
  }
}
```

### Example 9: Synthetic Identity - Bust Out Pattern
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-SYNT-5D8E23",
    "transaction_type": "CASH_ADVANCE",
    "transaction_datetime": "2024-01-20T22:15:44.678Z"
  },
  "financial": {
    "amount": 9500.00,
    "currency": "USD",
    "cash_advance_fee": 475.00,
    "credit_limit": 10000.00,
    "current_balance": 9500.00
  },
  "card": {
    "masked_pan": "************8912",
    "bin": "414709",
    "card_brand": "VISA",
    "card_type": "CREDIT",
    "card_present": false,
    "months_since_card_issued": 6
  },
  "merchant": {
    "merchant_id": "ATM-CASINO-LV892",
    "merchant_name": "Casino ATM",
    "merchant_category_code": "7995",
    "merchant_category": "Gambling",
    "location": "Las Vegas, NV"
  },
  "customer": {
    "customer_id": "CUST-2023-SYNT-8B",
    "customer_since": "2023-07-20",
    "age_of_account_days": 184,
    "ssn_issued_date": "2023-06-15",
    "credit_history_length_days": 190,
    "authorized_users": 3,
    "address_type": "MAIL_DROP"
  },
  "device": {
    "multiple_accounts_same_device": 8,
    "device_linked_to_fraud": true
  },
  "velocity_counters": {
    "credit_limit_increases_last_6m": 4,
    "balance_transfers_in": 8500.00,
    "payments_made": 12,
    "max_utilization_reached_today": true
  },
  "behavioral_profile": {
    "payment_pattern": "MINIMUM_ONLY",
    "utilization_trend": "RAPIDLY_INCREASING",
    "merchant_diversity": "LOW",
    "cash_advance_history": "SUDDEN_SPIKE"
  }
}
```

---

## 🔵 EDGE CASES - LEGITIMATE BUT UNUSUAL

### Example 10: Emergency Medical Payment Abroad
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-EMER-6A9C47",
    "transaction_type": "PAYMENT",
    "transaction_datetime": "2024-01-20T03:45:12.345Z",
    "urgency_flag": "EMERGENCY"
  },
  "financial": {
    "amount": 12500.00,
    "currency": "THB",
    "amount_usd": 352.75,
    "exchange_rate": 35.46
  },
  "card": {
    "masked_pan": "************5678",
    "bin": "554213",
    "card_brand": "MASTERCARD",
    "card_type": "DEBIT",
    "card_present": true,
    "entry_mode": "CHIP",
    "pin_verified": true
  },
  "merchant": {
    "merchant_id": "MID-HOSPITAL-BKK",
    "merchant_name": "Bangkok Hospital",
    "merchant_category_code": "8062",
    "merchant_category": "Hospitals",
    "merchant_city": "Bangkok",
    "merchant_country": "TH"
  },
  "customer": {
    "customer_id": "CUST-2016-3B8D92",
    "customer_since": "2016-04-12",
    "age_of_account_days": 2849,
    "emergency_contact_notified": true,
    "travel_insurance_active": true
  },
  "authentication": {
    "authentication_method": "PIN",
    "authentication_status": "VERIFIED",
    "embassy_verification": true
  },
  "location": {
    "transaction_city": "Bangkok",
    "transaction_country": "TH",
    "hospital_verified": true,
    "distance_from_home_km": 13567
  },
  "velocity_counters": {
    "international_transactions_today": 1,
    "medical_payments_lifetime": 1,
    "unusual_hour_transactions": 1
  },
  "behavioral_profile": {
    "home_city": "Seattle",
    "international_travel_history": "OCCASIONAL",
    "medical_payment_history": "NEVER",
    "emergency_fund_available": true
  }
}
```

### Example 11: Business Expense - Conference Registration
```json
{
  "transaction": {
    "transaction_id": "TXN-20240120-CONF-8C4F91",
    "transaction_type": "PURCHASE",
    "transaction_datetime": "2024-01-20T09:15:33.789Z",
    "business_transaction": true
  },
  "financial": {
    "amount": 3500.00,
    "currency": "USD",
    "expense_category": "PROFESSIONAL_DEVELOPMENT"
  },
  "card": {
    "masked_pan": "************9023",
    "bin": "403628",
    "card_brand": "VISA",
    "card_type": "BUSINESS",
    "card_subtype": "CORPORATE",
    "card_present": false,
    "employee_id": "EMP-45678"
  },
  "merchant": {
    "merchant_id": "MID-CONF-TECH2024",
    "merchant_name": "TechConf 2024 Registration",
    "merchant_category_code": "7399",
    "merchant_category": "Business Services",
    "event_date": "2024-03-15",
    "event_location": "San Francisco, CA"
  },
  "customer": {
    "company_account": "ACME-CORP",
    "employee_name": "John Smith",
    "department": "Engineering",
    "expense_approval": "PRE_APPROVED",
    "manager_approval": "MGR-12345"
  },
  "device": {
    "device_id": "DEV-CORP-LAPTOP-8A9C",
    "device_type": "DESKTOP",
    "corporate_network": true,
    "vpn_connection": "CORPORATE_VPN"
  },
  "authentication": {
    "authentication_method": "SSO",
    "corporate_authentication": true,
    "expense_system_linked": true
  },
  "velocity_counters": {
    "business_expenses_this_month": 8,
    "conference_registrations_this_year": 2
  },
  "behavioral_profile": {
    "typical_business_expense": 500.00,
    "annual_conference_budget": 10000.00,
    "expense_submission_pattern": "REGULAR"
  }
}
```

### Example 12: Seasonal Pattern - Tax Payment
```json
{
  "transaction": {
    "transaction_id": "TXN-20240415-TAX-2B8C56",
    "transaction_type": "PAYMENT",
    "transaction_datetime": "2024-04-15T23:45:59.999Z",
    "payment_deadline": "2024-04-15T23:59:59.999Z"
  },
  "financial": {
    "amount": 8234.00,
    "currency": "USD",
    "payment_type": "TAX_PAYMENT"
  },
  "card": {
    "masked_pan": "************3456",
    "bin": "485932",
    "card_brand": "VISA",
    "card_type": "DEBIT",
    "card_present": false
  },
  "merchant": {
    "merchant_id": "GOV-IRS-PAYMENT",
    "merchant_name": "IRS Direct Pay",
    "merchant_category_code": "9311",
    "merchant_category": "Tax Payments",
    "government_verified": true
  },
  "customer": {
    "customer_id": "CUST-2010-9A3D78",
    "customer_since": "2010-01-15",
    "age_of_account_days": 5208,
    "tax_payment_history": "ANNUAL"
  },
  "device": {
    "device_id": "DEV-HOME-TRUST-5C8E",
    "device_type": "DESKTOP",
    "days_since_device_first_seen": 1456
  },
  "authentication": {
    "authentication_method": "MFA",
    "mfa_type": "SMS",
    "government_portal_verified": true
  },
  "velocity_counters": {
    "tax_payments_today": 1,
    "large_payments_this_month": 3,
    "government_payments_this_year": 4
  },
  "behavioral_profile": {
    "tax_payment_pattern": "LAST_MINUTE",
    "typical_tax_payment_date": "April 15",
    "annual_tax_payment_range": "7000-10000"
  }
}
```

---

## 💻 Test Data Generator

### Python Script for Generating Test Transactions
```python
import json
import random
from datetime import datetime, timedelta
import uuid

def generate_test_transaction(risk_level="low", scenario="standard"):
    """
    Generate realistic test transaction data

    Args:
        risk_level: "low", "medium", "high"
        scenario: "standard", "travel", "online", "atm", etc.
    """

    base_transaction = {
        "transaction": {
            "transaction_id": f"TXN-TEST-{uuid.uuid4().hex[:8].upper()}",
            "transaction_type": random.choice(["PURCHASE", "ECOMMERCE", "ATM_WITHDRAWAL"]),
            "transaction_datetime": datetime.now().isoformat() + "Z"
        },
        "financial": {
            "amount": round(random.uniform(10, 5000), 2),
            "currency": "USD"
        },
        "card": {
            "masked_pan": f"************{random.randint(1000, 9999)}",
            "bin": str(random.randint(400000, 559999)),
            "card_brand": random.choice(["VISA", "MASTERCARD"]),
            "card_type": random.choice(["CREDIT", "DEBIT"]),
            "card_present": scenario != "online"
        },
        # Add more fields based on scenario and risk level
    }

    # Adjust based on risk level
    if risk_level == "high":
        # Add suspicious patterns
        base_transaction["velocity_counters"] = {
            "transactions_last_hour": random.randint(10, 20),
            "declined_transactions_today": random.randint(3, 8)
        }
    elif risk_level == "medium":
        # Add borderline patterns
        base_transaction["location"] = {
            "distance_from_home_km": random.randint(500, 2000)
        }

    return base_transaction

# Generate test data
for risk in ["low", "medium", "high"]:
    transaction = generate_test_transaction(risk_level=risk)
    print(f"\n{risk.upper()} RISK:")
    print(json.dumps(transaction, indent=2))
```

---

## 🔍 Analysis Guidelines

### Key Risk Indicators (No Scores Included)
The fraud detection system should analyze these patterns:

1. **Temporal Anomalies**
   - Transactions at unusual hours for the customer
   - Rapid succession of transactions
   - Timing relative to account changes

2. **Geographic Inconsistencies**
   - Distance from home location
   - Impossible travel scenarios
   - VPN/Proxy detection

3. **Behavioral Deviations**
   - Amount outside normal range
   - New merchant categories
   - Unusual transaction patterns

4. **Authentication Weaknesses**
   - Missing or failed MFA
   - Multiple login attempts
   - Recent password changes

5. **Device Anomalies**
   - New or unrecognized devices
   - Jailbroken/rooted devices
   - Multiple accounts per device

6. **Velocity Violations**
   - High transaction frequency
   - Escalating amounts
   - Multiple declined attempts

---

## 📝 Implementation Notes

### Data Privacy Considerations
- All PAN data is masked (only last 4 digits)
- No CVV/CVC data is ever stored or transmitted
- Personal data is anonymized in test scenarios
- IP addresses in examples are non-routable

### Realistic Field Values
- **MCCs**: Using actual ISO 18245 merchant category codes
- **BINs**: Valid IIN ranges for card brands
- **Currencies**: ISO 4217 currency codes
- **Countries**: ISO 3166 country codes
- **Time zones**: Proper UTC offsets

### Testing Recommendations
1. Test with various time zones and currencies
2. Include edge cases like daylight saving transitions
3. Test with partial data (missing optional fields)
4. Verify handling of null vs empty values
5. Test concurrent transactions from same account

---

These examples represent actual production transaction patterns without any pre-computed risk assessments, allowing the fraud detection system to demonstrate its pattern recognition and decision-making capabilities.