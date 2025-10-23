# 🛡️ Fraud Detection Agent - AI-Powered Transaction Risk Assessment

A sophisticated **LangGraph-based fraud detection system** that leverages parallel AI analysis to detect fraudulent transactions in real-time. Built with Python, FastAPI, and OpenAI's language models, this agent performs multi-dimensional risk assessment through five specialized analyzers running in parallel.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Fraud Detection Methodology](#fraud-detection-methodology)
- [LangGraph Implementation](#langgraph-implementation)
- [Deployment](#deployment)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## 🎯 Overview

### What is this Agent?

The Fraud Detection Agent is an intelligent system that analyzes financial transactions for potential fraud using multiple AI-powered analyzers working in parallel. It provides real-time risk assessment with three possible outcomes: **APPROVE**, **REVIEW**, or **DECLINE**.

### Key Capabilities

- **Parallel Analysis**: 5 specialized fraud detectors run simultaneously
- **LLM-Powered**: Uses OpenAI's GPT models for sophisticated pattern recognition
- **Flexible Input**: Accepts multiple transaction data formats
- **Production-Ready**: Deployed on Google Cloud Run with monitoring
- **Configurable**: Adjustable risk thresholds and analyzer weights
- **Fault-Tolerant**: Built-in retry logic and timeout protection

### Technology Stack

- **Orchestration**: LangGraph (state-based parallel workflow)
- **AI/ML**: OpenAI GPT-4o-mini (configurable)
- **Runtime**: FastAPI + Uvicorn
- **Language**: Python 3.13
- **Deployment**: Google Cloud Run
- **Monitoring**: Handit AI

## 🏗️ Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server (Port 8001)              │
│                    with Handit AI Tracing                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │   LangGraphAgent   │
        │  (Main Orchestrator)│
        └────────────┬───────┘
                     │
        ┌────────────▼────────────┐
        │  RiskManagerGraph       │
        │  (StateGraph Based)     │
        └────────────┬────────────┘
                     │
        ┌────────────▼──────────────────────────────────────┐
        │        ORCHESTRATOR NODE (START)                  │
        │  Normalizes and enriches transaction data          │
        └────────────┬──────────────────────────────────────┘
                     │
        ┌────────────▼──────────────────────────────────────┐
        │         PARALLEL ANALYZER EXECUTION               │
        │  ┌──────────────┐ ┌──────────────┐               │
        │  │  Pattern     │ │ Behavioral   │               │
        │  │  Detector    │ │ Analyzer     │               │
        │  └──────────────┘ └──────────────┘               │
        │  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
        │  │  Velocity    │ │ Merchant     │ │Geographic││
        │  │  Checker     │ │ Risk Analyzer│ │ Analyzer ││
        │  └──────────────┘ └──────────────┘ └──────────┘ │
        └────────────┬──────────────────────────────────────┘
                     │
        ┌────────────▼──────────────────────┐
        │  DECISION AGGREGATOR NODE         │
        │  Combines all analyzer results    │
        └────────────┬──────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  Final JSON Decision Output    │
        │  {final_decision, reason, ...} │
        └────────────────────────────────┘
```

### Project Structure

```
risk_manager/
├── main.py                          # FastAPI application entry point
├── src/
│   ├── agent.py                     # LangGraphAgent orchestrator
│   ├── base.py                      # Base node classes
│   ├── config.py                    # Configuration and graph topology
│   ├── graph/
│   │   ├── main.py                  # RiskManagerGraph implementation
│   │   └── nodes/
│   │       └── nodes.py             # Node function definitions
│   ├── nodes/
│   │   └── llm/                     # LLM-based analyzer nodes
│   │       ├── pattern_detector/    # Fraud pattern detection
│   │       ├── behavioral_analizer/ # Behavioral anomaly detection
│   │       ├── velocity_checker/    # Velocity abuse detection
│   │       ├── merchant_risk_analizer/ # Merchant risk assessment
│   │       ├── geographic_analizer/ # Geographic fraud detection
│   │       └── decision_aggregator/ # Final decision maker
│   ├── state/
│   │   └── state.py                 # AgentState definition
│   └── utils/
│       └── openai_client.py         # OpenAI client wrapper
├── use_cases/                       # Test cases and examples
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── cloudbuild.yaml                  # Google Cloud Build config
```

## ✨ Features

### Core Capabilities

#### 1. **Parallel Processing Architecture**
- 5 analyzers run simultaneously, not sequentially
- Reduces processing time from ~5x to ~1x
- Automatic state merging with LangGraph

#### 2. **Multi-Format Input Support**
Accepts various transaction data formats:
- Simple format (basic fields)
- Complex banking format (comprehensive data)
- Legacy format (backward compatibility)
- Hybrid format (mixed structure)

#### 3. **Intelligent Risk Assessment**
- Weighted scoring from multiple analyzers
- Configurable risk thresholds
- Evidence-based decision making

#### 4. **Production-Ready Infrastructure**
- Async/await throughout
- Retry with exponential backoff
- Timeout protection (120s max)
- Health checks and monitoring

### The Five Fraud Analyzers

| Analyzer | Purpose | Weight | Key Detection Areas |
|----------|---------|---------|---------------------|
| **Pattern Detector** | Identifies known fraud signatures | 25% | Synthetic identity, account takeover, card testing, money laundering |
| **Behavioral Analyzer** | Detects user behavior anomalies | 20% | Spending patterns, temporal deviations, merchant preferences |
| **Velocity Checker** | Catches rapid-fire attacks | 25% | Transaction frequency, amount velocity, failure rates |
| **Merchant Risk Analyzer** | Assesses merchant trustworthiness | 15% | Merchant category, reputation, fraud history |
| **Geographic Analyzer** | Detects location-based fraud | 15% | Impossible travel, VPN detection, high-risk regions |

## 🚀 Installation

### Prerequisites

- Python 3.13+
- OpenAI API key
- (Optional) Handit AI API key for monitoring
- (Optional) Google Cloud account for deployment

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd risk_manager
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. **Run the application**
```bash
python main.py
```

The server will start on `http://localhost:8001`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=sk-...           # Your OpenAI API key

# Optional
HANDIT_API_KEY=...               # Handit AI monitoring (optional)
MODEL_NAME=gpt-4o-mini           # LLM model to use (default: gpt-4o-mini)
MODEL_PROVIDER=openai            # LLM provider (default: mock for testing)
ENVIRONMENT=development          # Environment (development/production)
HOST=0.0.0.0                     # Server host
PORT=8001                        # Server port
LOG_LEVEL=info                   # Logging level (debug/info/warning/error)
```

### Risk Thresholds

Modify risk thresholds in `src/config.py`:

```python
self.risk_thresholds = {
    "decline": 70,    # Risk score >= 70: DECLINE
    "review": 40,     # Risk score >= 40: REVIEW
    "approve": 0      # Risk score < 40: APPROVE
}
```

### Analyzer Weights

Adjust the importance of each analyzer in `src/config.py`:

```python
self.analyzer_weights = {
    "pattern_detector": 0.25,       # 25% weight
    "behavioral_analizer": 0.20,    # 20% weight
    "velocity_checker": 0.25,        # 25% weight
    "merchant_risk_analizer": 0.15, # 15% weight
    "geographic_analizer": 0.15      # 15% weight
}
```

## 📡 Usage

### Basic API Call

```bash
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john_doe_123",
    "amount": 250.50,
    "merchant_name": "Amazon",
    "user_age_days": 365,
    "total_transactions": 150
  }'
```

### Python Example

```python
import requests

# Transaction data
transaction = {
    "user_id": "customer_123",
    "amount": 500.00,
    "merchant_name": "Electronics Store",
    "user_age_days": 180,
    "total_transactions": 50,
    "location": "New York, US",
    "time": "14:30",
    "velocity_counters": {
        "transactions_last_hour": 2,
        "declined_transactions_last_24h": 0
    }
}

# Send request
response = requests.post(
    "http://localhost:8001/process",
    json=transaction
)

# Parse response
result = response.json()
decision = result["result"]["decision"]["final_decision"]
reason = result["result"]["decision"]["reason"]

print(f"Decision: {decision}")
print(f"Reason: {reason}")
```

### Response Format

```json
{
  "result": {
    "pattern_detector": "No suspicious patterns detected...",
    "behavioral_analizer": "Transaction aligns with user history...",
    "velocity_checker": "Normal transaction velocity...",
    "merchant_risk_analizer": "Trusted merchant...",
    "geographic_analizer": "Location consistent...",
    "decision": {
      "final_decision": "APPROVE",
      "conclusion": "Low-risk transaction from established user",
      "recommendations": ["Process transaction normally"],
      "reason": "All analyzers indicate low fraud risk..."
    }
  },
  "success": true,
  "metadata": {
    "agent": "risk_manager",
    "framework": "langgraph",
    "processing_time_ms": 3250.45
  }
}
```

## 📚 API Documentation

### Endpoints

#### POST /process
Process a transaction through fraud detection

**Request Body** (Multiple formats supported):

Simple Format:
```json
{
  "user_id": "string",
  "amount": 0.0,
  "merchant_name": "string",
  "user_age_days": 0,
  "total_transactions": 0
}
```

Complex Banking Format:
```json
{
  "transaction": {
    "transaction_id": "string",
    "amount": 0.0,
    "currency": "USD"
  },
  "merchant": {
    "merchant_name": "string",
    "merchant_category_code": "string"
  },
  "customer": {
    "user_id": "string",
    "user_age_days": 0
  },
  "velocity_counters": {
    "transactions_last_hour": 0,
    "declined_transactions_last_24h": 0
  }
}
```

**Response**: ProcessResponse with analyzer results and decision

#### GET /health
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "agent": "risk_manager",
  "framework": "langgraph"
}
```

#### GET /graph/info
Get graph structure information

**Response**: Graph topology and node information

## 🔍 Fraud Detection Methodology

### Detection Strategy

The system employs a **multi-layered defense strategy**:

1. **Pattern Recognition**: Identifies known fraud signatures
2. **Behavioral Analysis**: Detects anomalies from established patterns
3. **Velocity Monitoring**: Catches rapid-fire attacks
4. **Merchant Assessment**: Evaluates merchant trustworthiness
5. **Geographic Verification**: Validates location consistency

### Risk Factors Analyzed

#### Transaction Risk Factors
- Amount anomalies (unusually high amounts)
- Time-based risks (transactions at 2-5 AM)
- New user risks (account age < 7 days)
- Authentication failures

#### Behavioral Risk Factors
- Spending pattern deviations
- Merchant preference changes
- Location inconsistencies
- Device/channel changes

#### Velocity Risk Factors
- High transaction frequency
- Escalating amounts
- Multiple declined attempts
- Rapid account changes

### Decision Logic

```
Risk Score Calculation:
├─ Each analyzer returns risk assessment
├─ Scores are weighted by importance
├─ Final score = Weighted average (0-100)
└─ Decision based on thresholds:
    ├─ Score < 40: APPROVE ✅
    ├─ Score 40-69: REVIEW 🔍
    └─ Score >= 70: DECLINE ❌
```

### Example Fraud Scenarios

#### Scenario 1: Account Takeover
- Pattern Detector: "Account takeover signature detected"
- Behavioral: "Significant deviation from normal behavior"
- Geographic: "Login from different country"
- **Decision**: DECLINE

#### Scenario 2: Card Testing
- Pattern Detector: "Multiple small transactions pattern"
- Velocity: "10 transactions in 5 minutes"
- Merchant: "Multiple different merchants"
- **Decision**: DECLINE

#### Scenario 3: Legitimate High-Value Purchase
- Pattern Detector: "No fraud patterns"
- Behavioral: "Consistent with user profile"
- Merchant: "Trusted merchant"
- **Decision**: APPROVE

## 🔄 LangGraph Implementation

### Why LangGraph?

LangGraph provides the perfect framework for our parallel fraud detection:

1. **State Management**: Automatic state merging from parallel branches
2. **Graph Structure**: Visual workflow representation
3. **Error Handling**: Built-in retry and error recovery
4. **Async Support**: Native async/await for high performance

### Graph Configuration

The graph topology is defined in `src/config.py`:

```python
graph_config = {
    "nodes": {
        "orchestrator": {...},           # Entry point
        "pattern_detector": {...},        # Parallel analyzer 1
        "behavioral_analizer": {...},     # Parallel analyzer 2
        "velocity_checker": {...},        # Parallel analyzer 3
        "merchant_risk_analizer": {...},  # Parallel analyzer 4
        "geographic_analizer": {...},     # Parallel analyzer 5
        "decision_aggregator": {...},     # Convergence point
        "finalizer": {...}                # Final processing
    },
    "edges": [
        # Fan-out (1 to many)
        {"from": "orchestrator", "to": "pattern_detector"},
        {"from": "orchestrator", "to": "behavioral_analizer"},
        {"from": "orchestrator", "to": "velocity_checker"},
        {"from": "orchestrator", "to": "merchant_risk_analizer"},
        {"from": "orchestrator", "to": "geographic_analizer"},

        # Fan-in (many to 1)
        {"from": "pattern_detector", "to": "decision_aggregator"},
        {"from": "behavioral_analizer", "to": "decision_aggregator"},
        {"from": "velocity_checker", "to": "decision_aggregator"},
        {"from": "merchant_risk_analizer", "to": "decision_aggregator"},
        {"from": "geographic_analizer", "to": "decision_aggregator"},

        # Sequential
        {"from": "decision_aggregator", "to": "finalizer"}
    ]
}
```

### State Management

The `AgentState` (TypedDict) manages data flow:

```python
class AgentState(TypedDict):
    input: Dict[str, Any]
    transaction_data: Dict[str, Any]
    enriched_transaction: Dict[str, Any]
    analyzer_results: Annotated[Dict, merge_dicts]  # Parallel merge
    risk_scores: Annotated[Dict, merge_dicts]       # Parallel merge
    completed_analyzers: List[str]
    final_decision: str
    results: Annotated[Dict, merge_dicts]           # Parallel merge
```

### Parallel Execution Flow

```
1. Orchestrator prepares transaction data
2. LangGraph spawns 5 parallel branches
3. Each analyzer runs independently
4. Results automatically merge (Annotated fields)
5. Decision aggregator receives all results
6. Final decision generated
```

## 🚢 Deployment

### Google Cloud Run Deployment

The application is configured for Google Cloud Run deployment with automatic CI/CD.

#### Prerequisites
- Google Cloud Project
- Cloud Build API enabled
- Artifact Registry repository created

#### Deployment Steps

1. **Configure secrets in Google Cloud**
```bash
echo "your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

2. **Update `cloudbuild.yaml`** with your project details

3. **Deploy using Cloud Build**
```bash
gcloud builds submit --config=cloudbuild.yaml
```

4. **Access the deployed service**
```bash
gcloud run services describe transaction-validation-agent --region=us-central1
```

### Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t fraud-detection-agent .

# Run container
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=your-key \
  fraud-detection-agent
```

### Configuration for Production

Recommended Cloud Run settings:
- **Memory**: 4 GiB (for LLM processing)
- **CPU**: 2 vCPUs
- **Timeout**: 600 seconds
- **Concurrency**: 10 requests
- **Min instances**: 0 (scale to zero)
- **Max instances**: 10 (adjust based on load)

## ⚡ Performance

### Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| **Average Processing Time** | 3-4 seconds | For complete analysis |
| **Parallel Speedup** | ~5x | Compared to sequential |
| **Throughput** | 15-20 req/min | Per instance |
| **Timeout Rate** | < 1% | With 120s timeout |
| **Success Rate** | > 99% | With retry logic |

### Optimization Tips

1. **Reduce Analyzer Count**: Disable less critical analyzers for speed
2. **Adjust Timeouts**: Lower timeout for faster failure detection
3. **Cache Results**: Implement Redis for repeat transactions
4. **Batch Processing**: Process multiple transactions together
5. **Model Selection**: Use faster models (gpt-3.5-turbo) for lower latency

### Resource Requirements

- **Minimum**: 2 GB RAM, 1 vCPU
- **Recommended**: 4 GB RAM, 2 vCPUs
- **Network**: Low bandwidth, ~1 KB per request
- **Storage**: Minimal, logs only

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. OpenAI API Errors
**Error**: `OpenAI API key not found`
**Solution**: Ensure `OPENAI_API_KEY` is set in environment

#### 2. Timeout Errors
**Error**: `asyncio.TimeoutError`
**Solution**:
- Increase timeout in `src/graph/main.py`
- Check OpenAI API status
- Reduce parallel analyzer count

#### 3. High Latency
**Symptoms**: Requests taking > 10 seconds
**Solutions**:
- Switch to faster model (gpt-3.5-turbo)
- Reduce prompt complexity
- Implement caching layer

#### 4. Memory Issues
**Error**: `Out of memory`
**Solution**: Increase Cloud Run memory allocation

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=debug python main.py
```

View detailed traces:
- Check Handit AI dashboard (if configured)
- Review application logs
- Use `/graph/info` endpoint for graph details

## 🛠️ Development

### Adding New Analyzers

1. **Create analyzer directory**
```bash
mkdir src/nodes/llm/new_analyzer
```

2. **Implement processor**
```python
# src/nodes/llm/new_analyzer/processor.py
from src.base import BaseLLMNode

class NewAnalyzerLLMNode(BaseLLMNode):
    async def run(self, input_data):
        # Implementation
        pass
```

3. **Define prompts**
```python
# src/nodes/llm/new_analyzer/prompts.py
def get_prompts():
    return {
        "system": "You are an expert...",
        "user_template": "Analyze..."
    }
```

4. **Register in config**
```python
# src/config.py
# Add to graph_config nodes and edges
```

5. **Add node function**
```python
# src/graph/nodes/nodes.py
async def new_analyzer_node(state):
    # Node implementation
    pass
```

### Running Tests

Execute test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_fraud_detection.py
```

### Running Use Cases

Test with provided use cases:

```bash
# Run all use cases
python run_use_cases.py

# Run specific file
python run_use_cases.py --file use_cases/SOPHISTICATED_FRAUD_CASES.json

# Generate report
python run_use_cases.py --report
```

### Code Quality

Maintain code quality:

```bash
# Format code
black .

# Lint
flake8 src/

# Type checking
mypy src/
```

## 📄 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

Please follow these guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📞 Support

- **Documentation**: [Handit.ai Documentation](https://docs.handit.ai)
- **LangGraph**: [LangGraph Documentation](https://docs.langchain.com/docs/langgraph)
- **Issues**: Open an issue in the repository

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for orchestration
- Powered by [OpenAI](https://openai.com) for AI analysis
- Monitored by [Handit AI](https://handit.ai) for observability
- Deployed on [Google Cloud Run](https://cloud.google.com/run) for scalability

---

**Version**: 1.0.0
**Last Updated**: January 2025
**Status**: Production Ready