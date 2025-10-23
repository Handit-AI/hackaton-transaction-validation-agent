# 🔄 Flexible API Input Examples

## Overview
The fraud detection API now accepts transaction data in **multiple flexible formats**. You can send transactions in whatever format is most convenient for your system.

---

## 📝 Input Formats Supported

### 1️⃣ **Complex Banking Transaction** (Full Production Format)
Send the complete transaction with all banking fields:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "transaction": {
        "transaction_id": "TXN-20240120-SUSPICIOUS-001",
        "transaction_type": "PURCHASE",
        "transaction_datetime": "2024-01-20T03:45:00.000Z"
    },
    "financial": {
        "amount": 4999.99,
        "currency": "USD"
    },
    "card": {
        "masked_pan": "************1234",
        "bin": "542418",
        "card_brand": "MASTERCARD",
        "card_type": "CREDIT"
    },
    "merchant": {
        "merchant_name": "CRYPTO EXCHANGE PRO",
        "merchant_category_code": "6051",
        "merchant_category": "Quasi Cash - Financial Institution"
    },
    "customer": {
        "customer_id": "CUST-COMPROMISED-001",
        "customer_since": "2018-02-20",
        "age_of_account_days": 2161
    },
    "device": {
        "device_id": "DEV-NEW-UNKNOWN",
        "device_type": "DESKTOP",
        "device_os": "Windows",
        "device_reputation_score": 12
    },
    "location": {
        "transaction_city": "Lagos",
        "transaction_country": "NG",
        "ip_country": "NG",
        "vpn_flag": true
    },
    "behavioral_profile": {
        "typical_transaction_amount": 45.0,
        "home_location": {
            "city": "Boston",
            "country": "US"
        }
    },
    "velocity_counters": {
        "transactions_last_hour": 5,
        "amount_last_hour": 8500.0,
        "declined_transactions_last_24h": 3
    },
    "risk_signals": {
        "ml_fraud_score": 0.89,
        "account_takeover_score": 0.91
    },
    "session": {
        "login_attempts": 4,
        "password_reset_flag": true,
        "mfa_completed": false
    }
}'
```

### 2️⃣ **Simple Transaction Format** (Quick Testing)
Send just the essential fields:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john_doe_123",
    "amount": 250.50,
    "merchant_name": "Amazon",
    "user_age_days": 365,
    "total_transactions": 150,
    "merchant_rating": 4.8,
    "merchant_fraud_reports": 0
}'
```

### 3️⃣ **Hybrid Format** (Mix of Simple and Complex)
Combine simple fields with complex objects:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.00,
    "user_id": "USER-456",
    "merchant": {
        "merchant_name": "Best Buy",
        "merchant_category_code": "5732"
    },
    "location": {
        "transaction_city": "New York",
        "transaction_country": "US"
    },
    "velocity_counters": {
        "transactions_today": 3,
        "amount_today": 2000.00
    }
}'
```

### 4️⃣ **Legacy Format** (Backward Compatible)
Using the original `input_data` field:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
        "user_id": "legacy_user",
        "amount": 99.99,
        "merchant": "Starbucks",
        "user_age_days": 90,
        "total_transactions": 45
    }
}'
```

### 5️⃣ **String Input** (JSON as String)
Send JSON as a string in `input_data`:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "{\"user_id\":\"user123\",\"amount\":75.00,\"merchant\":\"Target\"}"
}'
```

### 6️⃣ **Minimal Transaction** (Testing Defaults)
Send almost nothing and let the system use defaults:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00
}'
```

---

## 🎯 Field Mapping

The API intelligently maps fields from different formats:

| Complex Format | Simple Format | Maps To |
|---|---|---|
| `customer.customer_id` | `user_id` | Transaction user ID |
| `customer.age_of_account_days` | `user_age_days` | Account age |
| `financial.amount` | `amount` | Transaction amount |
| `merchant.merchant_name` | `merchant_name` | Merchant name |
| `location.transaction_city` | - | Location string |

---

## 📊 Example Responses

All formats return the same response structure:

```json
{
    "result": {
        "transaction_id": "TXN-ABC123",
        "decision": "APPROVE",
        "risk_score": 32.5,
        "confidence": 0.85,
        "processing_time_seconds": 3.245,
        "summary": {
            "critical_findings": [],
            "reasoning": "Low risk transaction from established user",
            "recommended_actions": []
        },
        "analyzer_breakdown": {
            "pattern_detector": 25,
            "behavioral_analyzer": 30,
            "velocity_checker": 35,
            "merchant_risk": 40,
            "geographic_analyzer": 30
        }
    },
    "success": true,
    "metadata": {
        "agent": "risk_manager",
        "framework": "langgraph",
        "processing_time_ms": 3245.67
    }
}
```

---

## 🧪 Testing Different Risk Levels

### Low Risk (Expected: APPROVE)
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "trusted_customer",
    "user_age_days": 1000,
    "total_transactions": 500,
    "amount": 50.00,
    "merchant_name": "Walmart",
    "merchant_rating": 4.5,
    "merchant_fraud_reports": 0
}'
```

### Medium Risk (Expected: REVIEW)
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "new_customer",
    "user_age_days": 30,
    "total_transactions": 5,
    "amount": 1000.00,
    "merchant_name": "Electronics Store",
    "merchant_rating": 3.0,
    "merchant_fraud_reports": 10,
    "location": {
        "transaction_country": "MX"
    }
}'
```

### High Risk (Expected: DECLINE)
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "suspicious_user",
    "user_age_days": 1,
    "total_transactions": 0,
    "amount": 5000.00,
    "time": "03:00",
    "merchant": {
        "merchant_name": "CRYPTO EXCHANGE",
        "merchant_category_code": "6051"
    },
    "location": {
        "transaction_country": "NG",
        "vpn_flag": true
    },
    "velocity_counters": {
        "transactions_last_hour": 10,
        "declined_transactions_last_24h": 5
    }
}'
```

---

## 🔧 Python Examples

### Using requests library:

```python
import requests
import json

# Simple format
simple_transaction = {
    "user_id": "python_user",
    "amount": 199.99,
    "merchant_name": "Amazon"
}

# Complex format
complex_transaction = {
    "transaction": {
        "transaction_id": "TXN-PYTHON-001",
        "transaction_type": "PURCHASE"
    },
    "financial": {
        "amount": 199.99,
        "currency": "USD"
    },
    "merchant": {
        "merchant_name": "Amazon",
        "merchant_category_code": "5999"
    }
}

# Send request
response = requests.post(
    "http://localhost:8000/process",
    json=simple_transaction  # or complex_transaction
)

result = response.json()
print(f"Decision: {result['result']['decision']}")
print(f"Risk Score: {result['result']['risk_score']}")
```

---

## 🌟 Benefits of Flexible Input

1. **Migration Friendly**: Gradually migrate from simple to complex formats
2. **Testing Convenience**: Quick tests with minimal data
3. **Integration Flexibility**: Different systems can use different formats
4. **Backward Compatible**: Old integrations continue to work
5. **Default Handling**: Missing fields get sensible defaults

---

## 📌 Important Notes

- **Transaction ID**: Auto-generated if not provided
- **Missing Fields**: System uses sensible defaults
- **Field Priority**: Structured fields override simple fields
- **Validation**: Basic validation ensures minimum required data
- **Case Sensitivity**: Field names are case-sensitive

---

## 🚀 Quick Start

1. **Minimal Test** (just to see it work):
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'
```

2. **Real-world Test**:
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "CUST-001",
    "amount": 250.00,
    "merchant_name": "Best Buy",
    "user_age_days": 180,
    "total_transactions": 25,
    "merchant_rating": 4.2,
    "merchant_fraud_reports": 2
}'
```

The API will process your transaction through the fraud detection system regardless of which format you use!