#!/usr/bin/env python3
"""
Quick test script for the fraud detection system
Uses realistic transaction examples to test the multi-agent analysis
"""

import asyncio
import json
from src.config import Config
from src.agent import LangGraphAgent

# Test transaction - Regular coffee purchase (low risk)
COFFEE_TRANSACTION = {
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
        "card_present": True,
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

# Test transaction - Account takeover pattern (high risk)
ACCOUNT_TAKEOVER = {
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
        "card_present": False
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
        "security_questions_reset": True
    },
    "device": {
        "device_id": "DEV-UNKNOWN-NEW-8C4F",
        "device_type": "MOBILE",
        "device_os": "Android",
        "device_os_version": "14",
        "device_jailbroken": True,
        "days_since_device_first_seen": 0,
        "sim_changed_recently": True
    },
    "authentication": {
        "authentication_method": "PASSWORD",
        "mfa_bypassed": True,
        "bypass_reason": "RECOVERY_CODE",
        "unusual_login_pattern": True
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
        "account_takeover_signals": True,
        "unusual_navigation_pattern": True,
        "direct_transfer_attempt": True
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

# Test transaction - International travel (medium risk)
INTERNATIONAL_TRAVEL = {
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
        "card_present": True,
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
        "international_travel_flag": False
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


async def test_transaction(transaction_data: dict, scenario_name: str):
    """Test a single transaction through the fraud detection system"""

    print(f"\n{'='*60}")
    print(f"🧪 Testing Scenario: {scenario_name}")
    print(f"{'='*60}")
    print(f"Transaction ID: {transaction_data['transaction']['transaction_id']}")
    print(f"Type: {transaction_data['transaction']['transaction_type']}")
    print(f"Amount: {transaction_data['financial']['currency']} {transaction_data['financial']['amount']}")

    # Initialize the agent
    config = Config()
    agent = LangGraphAgent(config)

    try:
        # Process the transaction
        print("\n⚡ Processing through fraud detection system...")
        result = await agent.execute(transaction_data)

        # Display results
        print("\n📊 RESULTS:")
        print("-" * 40)

        if isinstance(result, dict):
            # Check for the final decision
            if 'decision' in result:
                decision = result['decision']
                if isinstance(decision, dict):
                    print(f"\n🎯 Final Decision: {decision.get('final_decision', 'UNKNOWN')}")
                    print(f"📝 Conclusion: {decision.get('conclusion', 'No conclusion')}")

                    if 'recommendations' in decision:
                        print("\n💡 Recommendations:")
                        for rec in decision.get('recommendations', []):
                            print(f"  • {rec}")

                    print(f"\n📋 Reason: {decision.get('reason', 'No reason provided')}")
                else:
                    print(f"\n🎯 Decision: {decision}")

            # Show analyzer results
            print("\n🔍 Analyzer Outputs:")
            for analyzer in ['pattern_detector', 'behavioral_analizer', 'velocity_checker',
                           'merchant_risk_analizer', 'geographic_analizer']:
                if analyzer in result:
                    analyzer_result = str(result[analyzer])
                    print(f"\n{analyzer}:")
                    print(f"  {analyzer_result[:200]}..." if len(analyzer_result) > 200 else f"  {analyzer_result}")
        else:
            print(f"Result: {result}")

    except Exception as e:
        print(f"\n❌ Error processing transaction: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all test scenarios"""

    print("\n" + "="*60)
    print("🏦 FRAUD DETECTION SYSTEM TEST")
    print("="*60)
    print("Testing multi-agent parallel analysis with realistic transactions")

    # Test different risk scenarios
    test_cases = [
        (COFFEE_TRANSACTION, "☕ Low Risk - Morning Coffee"),
        (INTERNATIONAL_TRAVEL, "✈️ Medium Risk - International Travel"),
        (ACCOUNT_TAKEOVER, "⚠️ High Risk - Account Takeover Pattern")
    ]

    for transaction, scenario in test_cases:
        await test_transaction(transaction, scenario)
        print("\n" + "="*60)

    print("\n✅ All test scenarios completed!")


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())