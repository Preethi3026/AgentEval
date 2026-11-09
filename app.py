import streamlit as st
import ollama
import time
import pandas as pd
import re
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AgentEval",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 AgentEval")
st.caption("AI Model Evaluation & Benchmarking Platform")

st.write(
    "Compare AI models using accuracy, response time "
    "and question-level evaluation."
)

# ==========================================
# LOAD HR POLICY
# ==========================================

policy_path = Path(__file__).parent / "hr_policy.txt"

if policy_path.is_file():
    policy_document = policy_path.read_text(encoding="utf-8")
else:
    policy_document = ""


# ==========================================
# RULE-BASED EVALUATION
# ==========================================

def check_required_facts(answer, fact_groups):

    answer = " ".join(answer.lower().split())
    missing = []

    for group in fact_groups:

        alternatives = [
            " ".join(phrase.strip().lower().split())
            for phrase in group.split("|")
            if phrase.strip()
        ]

        matched = any(
            phrase in answer
            for phrase in alternatives
        )

        # Handle missing policy information

        information_related = any(
            term in group.lower()
            for term in [
                "information",
                "not mentioned",
                "not specified"
            ]
        )

        if not matched and information_related:

            unavailable_phrases = [
                "not mentioned",
                "does not mention",
                "doesn't mention",
                "not specified",
                "not stated",
                "not enough information",
                "don't have enough information",
                "do not have enough information",
                "no information",
                "insufficient information",
                "not provided",
                "cannot determine"
            ]

            matched = any(
                phrase in answer
                for phrase in unavailable_phrases
            )

        # Handle five-day vacation carryover limit

        if not matched and (
            "5 days" in group.lower()
            or "maximum of 5" in group.lower()
        ):

            matched = bool(
                re.search(
                    r"\b5\b.{0,60}\b(?:unused\s+)?vacation\s+days\b",
                    answer
                )
                or re.search(
                    r"(?:maximum|limit).{0,60}\b5\b",
                    answer
                )
                or re.search(
                    r"\b5\s+days\b",
                    answer
                )
                or re.search(
                    r"\bfive\s+days\b",
                    answer
                )
            )

        # Handle rejection of carrying over 10 days

        if not matched and (
            "cannot carry over 10" in group.lower()
            or "10 days" in group.lower()
        ):

            matched = any(
                phrase in answer
                for phrase in [
                    "more than 5",
                    "maximum of 5",
                    "maximum carryover limit",
                    "cannot carry over 10",
                    "cannot carry forward 10",
                    "limit is 5",
                    "maximum is 5"
                ]
            )

        if not matched:
            missing.append(group)

    return len(missing) == 0, missing


# ==========================================
# 1. CONFIGURE YOUR AI AGENT
# ==========================================

st.header("1. Configure your AI agent")

system_prompt = st.text_area(
    "System prompt",
    value=(
        "You are a professional HR Policy Assistant. "
        "Answer using only the company HR policy. "
        "Never invent information. If information is missing, "
        "say you do not have enough information."
    ),
    height=120
)


# ==========================================
# 2. TEST QUESTIONS
# ==========================================

st.header("2. Test questions")

test_questions = st.text_area(
    "Enter one question per line",
    height=150
)


# ==========================================
# 3. EXPECTED ANSWERS
# ==========================================

st.header("3. Expected answers")

expected_answers = st.text_area(
    "Enter one expected answer per line in the same order",
    height=150
)


# ==========================================
# 4. REQUIRED FACTS
# ==========================================

st.header("4. Required facts for rule-based evaluation")

st.write(
    "Enter one line per question. Separate required facts "
    "with semicolons. Use | for alternative phrases."
)

required_facts_text = st.text_area(
    "Required facts (one line per question)",
    height=150
)


# ==========================================
# 5. SELECT AI MODELS
# ==========================================

st.header("5. Select models")

available_models = [
    "llama3.1:latest",
    "qwen2.5:3b"
]

selected_models = st.multiselect(
    "Choose AI models",
    available_models,
    default=available_models
)


# ==========================================
# RUN EVALUATION
# ==========================================

if st.button(
    "🚀 Compare Models",
    type="primary",
    use_container_width=True
):

    questions = [
        q.strip()
        for q in test_questions.splitlines()
        if q.strip()
    ]

    expected = [
        a.strip()
        for a in expected_answers.splitlines()
        if a.strip()
    ]

    fact_lines = [
        line.strip()
        for line in required_facts_text.splitlines()
        if line.strip()
    ]

    if not system_prompt.strip():

        st.error("Please enter a system prompt.")

    elif not questions:

        st.error("Please enter test questions.")

    elif len(questions) != len(expected):

        st.error(
            "Question count and expected answer count must match."
        )

    elif len(questions) != len(fact_lines):

        st.error(
            "Enter exactly one required-facts line per question."
        )

    elif not policy_document.strip():

        st.error(
            "HR policy document not found. Check hr_policy.txt."
        )

    elif not selected_models:

        st.error("Please select at least one model.")

    else:

        all_results = {}

        # ==========================================
        # EVALUATE EACH MODEL
        # ==========================================

        for model in selected_models:

            st.divider()

            st.header(f"📊 Evaluation: {model}")

            judge_results = []
            rule_results = []
            combined_results = []
            response_times = []

            # ==========================================
            # EVALUATE EACH QUESTION
            # ==========================================

            for number, (
                question,
                expected_answer,
                fact_line
            ) in enumerate(
                zip(questions, expected, fact_lines),
                start=1
            ):

                fact_groups = [
                    group.strip()
                    for group in fact_line.split(";")
                    if group.strip()
                ]

                with st.expander(
                    f"Test Case {number}: {question}",
                    expanded=True
                ):

                    try:

                        # Generate model answer

                        start_time = time.perf_counter()

                        with st.spinner(
                            f"{model} is generating an answer..."
                        ):

                            response = ollama.chat(
                                model=model,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": (
                                            system_prompt
                                            + "\n\nCompany HR Policy:\n"
                                            + policy_document
                                        )
                                    },
                                    {
                                        "role": "user",
                                        "content": question
                                    }
                                ]
                            )

                        answer = response["message"]["content"]

                        elapsed = (
                            time.perf_counter() - start_time
                        )

                        response_times.append(elapsed)

                        # ==================================
                        # RULE-BASED EVALUATION
                        # ==================================

                        rule_passed, missing_facts = (
                            check_required_facts(
                                answer,
                                fact_groups
                            )
                        )

                        # ==================================
                        # LLM JUDGE EVALUATION
                        # ==================================

                        with st.spinner(
                            "LLM Judge is evaluating..."
                        ):

                            judge_response = ollama.chat(
                                model="llama3.1:latest",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": (
                                            "You are an expert AI evaluation judge. "
                                            "Compare the AI answer with the expected "
                                            "answer by meaning, not exact wording. "
                                            "Accept equivalent factual explanations. "
                                            "Accept correct answers that contain "
                                            "additional relevant details. "
                                            "For missing policy information, accept "
                                            "a clear statement that the information "
                                            "is unavailable. "
                                            "For a question about carrying over "
                                            "10 vacation days, accept an answer "
                                            "that correctly states the five-day "
                                            "maximum limit and rejects or rules "
                                            "out carrying over 10 days. "
                                            "Do not require exact phrases. "
                                            "Return only PASS or FAIL."
                                        )
                                    },
                                    {
                                        "role": "user",
                                        "content": (
                                            f"Question: {question}\n\n"
                                            f"Expected answer: {expected_answer}\n\n"
                                            f"AI answer: {answer}\n\n"
                                            "Is the AI answer factually correct "
                                            "and equivalent to the expected answer? "
                                            "Return only PASS or FAIL."
                                        )
                                    }
                                ]
                            )

                        verdict = (
                            judge_response["message"]["content"]
                            .strip()
                            .upper()
                        )

                        judge_passed = verdict.startswith("PASS")

                        # Both checks must pass

                        combined_passed = (
                            judge_passed and rule_passed
                        )

                        judge_results.append(judge_passed)
                        rule_results.append(rule_passed)
                        combined_results.append(combined_passed)

                        # ==================================
                        # DISPLAY ANSWERS
                        # ==================================

                        st.write("**AI Answer**")

                        st.info(answer)

                        st.write("**Expected Answer**")

                        st.write(expected_answer)

                        col1, col2 = st.columns(2)

                        with col1:

                            if judge_passed:
                                st.success("LLM Judge: PASS")
                            else:
                                st.error("LLM Judge: FAIL")

                        with col2:

                            if rule_passed:
                                st.success("Rule-Based Check: PASS")
                            else:
                                st.error("Rule-Based Check: FAIL")

                                st.write(
                                    "Missing required facts:",
                                    missing_facts
                                )

                        if combined_passed:

                            st.success("Combined Result: PASS")

                        else:

                            st.error("Combined Result: FAIL")

                        st.caption(
                            f"Response time: {elapsed:.2f} seconds"
                        )

                    except Exception as error:

                        st.error(
                            f"Evaluation error: {error}"
                        )

                        judge_results.append(False)
                        rule_results.append(False)
                        combined_results.append(False)

            # ==========================================
            # MODEL PERFORMANCE
            # ==========================================

            total = len(questions)

            average_time = (
                sum(response_times) / len(response_times)
                if response_times else 0
            )

            all_results[model] = {

                "LLM Judge Passed": sum(judge_results),

                "Rule-Based Passed": sum(rule_results),

                "Combined Passed": sum(combined_results),

                "Total": total,

                "Accuracy": (
                    sum(combined_results) / total * 100
                ),

                "Average Response Time": average_time
            }

        # ==========================================
        # PERFORMANCE DASHBOARD
        # ==========================================

        st.divider()

        st.header("🏆 AgentEval Performance Dashboard")

        comparison_data = []

        for model, data in all_results.items():

            comparison_data.append({

                "Model": model,

                "LLM Judge Passed": data["LLM Judge Passed"],

                "Rule-Based Passed": data["Rule-Based Passed"],

                "Combined Passed": data["Combined Passed"],

                "Combined Accuracy (%)": round(
                    data["Accuracy"], 2
                ),

                "Avg Response Time (seconds)": round(
                    data["Average Response Time"], 2
                )

            })

        comparison_df = pd.DataFrame(comparison_data)

        best_model = max(
            all_results,
            key=lambda model: all_results[model]["Accuracy"]
        )

        models_with_times = [
            model
            for model in all_results
            if all_results[model]["Average Response Time"] > 0
        ]

        fastest_model = (
            min(
                models_with_times,
                key=lambda model: (
                    all_results[model]["Average Response Time"]
                )
            )
            if models_with_times
            else "N/A"
        )

        # ==========================================
        # DASHBOARD METRICS
        # ==========================================

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Models Evaluated",
            len(all_results)
        )

        col2.metric(
            "Best Combined Accuracy",
            f'{all_results[best_model]["Accuracy"]:.1f}%'
        )

        col3.metric(
            "Fastest Model",
            fastest_model
        )

        # ==========================================
        # COMPARISON TABLE
        # ==========================================

        st.subheader("📋 Model Comparison")

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )

        # ==========================================
        # ACCURACY CHART
        # ==========================================

        st.subheader("📈 Combined Accuracy Comparison")

        accuracy_chart = comparison_df.set_index("Model")[
            ["Combined Accuracy (%)"]
        ]

        st.bar_chart(accuracy_chart)

        # ==========================================
        # RESPONSE TIME CHART
        # ==========================================

        st.subheader("⚡ Response Time Comparison")

        response_chart = comparison_df.set_index("Model")[
            ["Avg Response Time (seconds)"]
        ]

        st.bar_chart(response_chart)

        # ==========================================
        # WINNING MODEL
        # ==========================================

        st.success(
            f"🏆 Best combined accuracy: {best_model}"
        )

        if fastest_model != "N/A":

            st.info(
                f"⚡ Fastest model: {fastest_model}"
            )

        # ==========================================
        # EXPORT RESULTS
        # ==========================================

        st.divider()

        st.subheader("📥 Download Evaluation Results")

        csv_data = comparison_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name="agenteval_results.csv",
            mime="text/csv"
        )

        st.caption(
            "Combined PASS requires both the LLM Judge "
            "and Rule-Based Check to pass. Results may vary "
            "slightly between model runs."
        )
