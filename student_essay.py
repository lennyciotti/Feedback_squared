import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ OpenAI API key is loaded!")
else:
    print("❌ OpenAI API key NOT loaded.")

client = OpenAI()
def text_generation(
    system_role: str,
    user_msg: str,
    prompt: str,
    sections: dict | None = None,
    model: str = "gpt-4o-mini",
    temperature: float = 1.0,
):
    user_parts = [prompt]
    for label, content in (sections or {}).items():
        user_parts.append(f"{label}:\n{content}")
    user_msg = "\n\n".join(user_parts)

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_msg},
        ],
        temperature=temperature,
    )
    text = (getattr(resp, "output_text", "") or "").strip()
    usage = getattr(resp, "usage", None)
    if usage is not None and not isinstance(usage, dict):
        usage = getattr(usage, "__dict__", None)
    return text, usage


def build_student_agent(grade_level: str, subject: str, assignment_type: str, topic: str) -> str:
    """
    Build a student persona for role-based generation.
    Keeps voice/level in the system message and defers specifics to the prompt.
    """
    return (
        f"You are a {grade_level} student completing a {assignment_type} for your {subject} class on the topic of '{topic}'. "
    
    )
def competency_level(knowledge_level: str, grammar_level: str) -> str:
    levels = {
        "failing": "You show little to no understanding of the subject matter",
        "beginner": "You demonstrate a basic understanding of the subject matter",
        "intermediate": "You have a good grasp of the subject matter and can apply concepts effectively",
        "advanced": "You have a deep understanding of the subject matter and can analyze complex topics",
    }

    grammar_levels = {
        "poor": "your grammar is poor and contains many errors",
        "fair": "your grammar is acceptable but contains some errors",
        "good": "your grammar is competent with only minor errors",
        "excellent": "your grammar is highly competent with no noticeable errors",
    }

    knowledge_desc = levels.get(knowledge_level.lower(), "your subject knowledge level is unrecognized")
    grammar_desc = grammar_levels.get(grammar_level.lower(), "your grammar level is unrecognized")

    return f"{knowledge_desc}, and {grammar_desc}."
    
sample_prompt = "write an essay. Make it 5 to 7 paragraphs, it should have an introduction, a thesis and a conclusion."   
student_agent = build_student_agent('10th grade', 'English', 'essay', 'The American Revolution')
#print(student_agent)
#essay_prompt = text_generation(student_agent)
competent_student = competency_level('advanced', 'excellent')
#print(competent_student)

def essay_gen(n, topic: str, grade_level: str, subject: str, assignment_type: str, knowledge_level: str, grammar_level: str, prompt: str, model="gpt-4o-mini"):
    topic_clean = topic.lower().replace(" ", "_")
    student_agent = build_student_agent(grade_level, subject, assignment_type, topic)
    student_competency = competency_level(knowledge_level, grammar_level)

    essay_vars = []

    for i in range(n):
        essay_text, _ = text_generation(
            system_role=student_agent,
            user_msg=student_competency,
            prompt=prompt,
            model=model,
        )
        var_name = f"essay_{topic_clean}_{i}"
        essay_vars.append((var_name, essay_text))

    # Save to .py file
    filename = f"essays_{topic_clean}.py"
    with open(filename, "w", encoding="utf-8") as f:
        for var_name, essay_text in essay_vars:
            f.write(f'{var_name} = """{essay_text}"""\n\n')

    print(f"✅ Saved {n} essays to {filename}")
essay_gen(
    n=3,
    topic="The American Revolution",
    grade_level="10th grade",
    subject="English",
    assignment_type="essay",
    knowledge_level="advanced",
    grammar_level="excellent",
    prompt="Write an essay. Make it 5 to 7 paragraphs, with an introduction, thesis, and conclusion."
)