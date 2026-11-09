# 🧪 AgentEval – AI Model Evaluation & Benchmarking Platform

AgentEval is a local AI model evaluation platform that compares different Large Language Models (LLMs) using automated test cases, LLM-as-a-Judge, rule-based validation, response-time measurement, and performance metrics.

The project helps evaluate AI model responses before switching models by measuring answer correctness, required information, and response speed.

## 🚀 Features

- **Multi-model comparison:** Evaluate Llama 3.1 and Qwen 2.5.
- **LLM-as-a-Judge:** Use an AI judge to assess the correctness of generated answers.
- **Rule-based evaluation:** Verify whether responses contain required facts.
- **Combined evaluation:** Combine both evaluation methods to determine PASS or FAIL.
- **Response-time tracking:** Measure how long each model takes to generate a response.
- **Performance dashboard:** Compare model accuracy and response times.
- **CSV export:** Download evaluation results for further analysis.
- **Local execution:** Run models locally using Ollama.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Interactive web interface |
| Ollama | Run local language models |
| Llama 3.1 | AI evaluation judge and tested model |
| Qwen 2.5 | Tested language model |
| Pandas | Results and data handling |

## 🏗️ How It Works

1. Configure the AI agent using a system prompt and HR policy document.
2. Provide test questions and expected answers.
3. Select the language models to evaluate.
4. Each selected model generates answers.
5. The LLM judge evaluates semantic correctness.
6. The rule-based evaluator checks required facts.
7. The combined evaluator determines the final PASS or FAIL result.
8. The dashboard displays accuracy and response-time comparisons.
9. Export evaluation results as a CSV file.

## 📊 Evaluation Results

The application was tested using eight HR policy test cases.

| Metric | Llama 3.1 | Qwen 2.5 |
|---|---:|---:|
| Test cases | 8 | 8 |
| LLM Judge Pass | 8/8 | 8/8 |
| Rule-Based Pass | 8/8 | 8/8 |
| Combined Pass | 8/8 | 8/8 |
| Combined Accuracy | 100% | 100% |
| Average Response Time | ~3.63 sec | ~6.97 sec |

**Observation:** Both models achieved 100% combined accuracy on the configured test suite. Llama 3.1 had the lower average response time in this particular evaluation.

*Note: These results represent one evaluation run using eight manually defined test cases, not a general performance guarantee.*

## 💻 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Preethi3026/AgentEval.git
cd AgentEval
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install streamlit ollama pandas
```

### 4. Install Ollama

Install Ollama and ensure its local service is running.

### 5. Download the models

```bash
ollama pull llama3.1
ollama pull qwen2.5:3b
```

### 6. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

## 📁 Project Structure

```text
AgentEval/
│
├── app.py
├── hr_policy.txt
├── .gitignore
└── README.md
```

## 🎯 Project Objective

The objective of AgentEval is to build a practical evaluation framework that helps developers assess AI model responses, identify performance differences, and make more informed model-selection decisions.

## 🔮 Future Improvements

- Support additional LLM providers and models.
- Expand automated test-case generation.
- Add more evaluation metrics.
- Support multiple knowledge documents.
- Introduce historical evaluation tracking.
- Improve benchmark reporting.

## 👩‍💻 Author

**Preethi Priya**

Master's Student – Big Data & Artificial Intelligence

GitHub: https://github.com/Preethi3026

LinkedIn: https://www.linkedin.com/in/preethipriya/

---

⭐ If you find this project interesting, feel free to explore the repository!