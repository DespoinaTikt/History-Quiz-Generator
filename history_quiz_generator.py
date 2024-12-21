import openai
import streamlit as st
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_questions(topic, difficulty):
    """Generate three multiple-choice questions for a given topic and difficulty."""
    messages = [
        {
            "role": "system",
            "content": "You are a history expert that generates multiple-choice questions with 4 options per question."
        },
        {
            "role": "user",
            "content": f"Generate three multiple-choice questions about {topic} at a {difficulty} level. Each question should have 4 options, and mark the correct answer with an asterisk (*).."
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message['content']

def parse_questions(raw_text):
    """Parse the raw text into structured questions and options."""
    questions = raw_text.split("\n\n")  # Split by double newlines
    parsed_questions = []
    for question in questions:
        lines = question.strip().split("\n")
        if len(lines) < 2:  # Ensure at least one question and one option exist
            continue
        question_text = lines[0].strip()  # First line is the question
        options = []
        for line in lines[1:]:  # Following lines are the options
            if line.startswith("*"):  # Correct answer is marked with *
                correct_answer = line[1:].strip()  # Remove the asterisk
                options.append(correct_answer)
            elif line.endswith("*"):
                correct_answer = line[:-1].strip()
                options.append(correct_answer)
            else:
                options.append(line.strip())
        parsed_questions.append({
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer
        })
    return parsed_questions

# Streamlit UI
st.title("🏛️ History Quiz Generator")

# Input field for topic
topic = "History"

difficulty = st.selectbox(
    "Select difficulty level:",
    ["Easy", "Medium", "Hard"],
    index=0 
)

if "questions" not in st.session_state:
    st.session_state.questions = None
if "answers" not in st.session_state:
    st.session_state.answers = {}

if st.button("Generate Questions"):
    try:
        raw_questions = generate_questions(topic, difficulty)
        st.session_state.questions = parse_questions(raw_questions)
        st.session_state.answers = {idx: None for idx in range(len(st.session_state.questions))}
    except Exception as e:
        st.error(f"Error generating questions: {e}")

if st.session_state.questions:
    st.subheader("Answer the Questions")
    for idx, q in enumerate(st.session_state.questions):
        st.write(f"**Question {idx + 1}:** {q['question']}")
        st.session_state.answers[idx] = st.radio(
            f"Choose an answer for Question {idx + 1}:",
            q["options"],
            key=f"answer_{idx}"
        )
        st.write("---")

    if st.button("Submit Answers"):
        score = 0
        st.subheader("Results")
        for idx, q in enumerate(st.session_state.questions):
            selected = st.session_state.answers[idx]
            correct = q['correct_answer']
            if selected == correct:
                score += 1
                st.write(f"✅ **Question {idx + 1}:** Correct! The answer is `{correct}`.")
            else:
                st.write(f"❌ **Question {idx + 1}:** Incorrect. You chose `{selected}`; the correct answer is `{correct}`.")
        st.write(f"**Your Score: {score}/{len(st.session_state.questions)}**")
