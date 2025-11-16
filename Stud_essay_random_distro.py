import random
import uuid
import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

# --- Environment Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ OpenAI API key is loaded!")
else:
    print("❌ OpenAI API key NOT loaded.")

client = OpenAI(
    api_key=api_key,
    base_url="https://us.api.openai.com/v1"
)

# --- Knowledge, Grammar, Flow Levels ---

knowledge_levels = {
    1: "no knowledge",
    2: "superficial knowledge",
    3: "medium knowledge",
    4: "deep knowledge",
    5: "deep knowledge with high ability for analysis"
}

grammar_levels = {
    1: "terrible grammar and spelling mistakes",
    2: "bad grammar",
    3: "decent grammar but very basic structure",
    4: "good grammar and structure",
    5: "great form, grammar and a broad vocabulary"
}

flow_levels = {
    1: "poor flow and organization. There is no thesis",
    2: "weak flow with some organization issues, the thesis is unclear",
    3: "adequate flow and organization, the thesis is in the first paragraph and the conclusion is in the last",
    4: "good flow and well-organized. The thesis is clear and the conclusion summarizes the main points. The ideas flow logically from paragraph to paragraph",
    5: "excellent flow and highly organized. The thesis is compelling and well-placed, and the conclusion effectively reinforces the main arguments. Transitions between paragraphs are smooth and enhance readability."
}

# --- Sampling Functions ---

def sample_knowledge(n):
    return [max(1, min(5, round(random.gauss(mu=2.5, sigma=1)))) for _ in range(n)]

def sample_grammar_from_knowledge(k):
    return max(1, min(5, k + random.choice([-1, 0, 1])))

def sample_flow_from_knowledge(k):
    return max(1, min(5, k + random.choice([-1, 0, 1])))

def generate_level_triplets(n):
    triplets = []
    knowledge_samples = sample_knowledge(n)
    for k in knowledge_samples:
        g = sample_grammar_from_knowledge(k)
        f = sample_flow_from_knowledge(k)
        triplets.append({
            "knowledge_level": k,
            "knowledge_desc": knowledge_levels[k],
            "grammar_level": g,
            "grammar_desc": grammar_levels[g],
            "flow_level": f,
            "flow_desc": flow_levels[f]
        })
    return triplets

# --- OpenAI Text Generation ---

def text_generation(system_role: str, user_msg: str, prompt: str,
                    sections: dict | None = None,
                    model: str = "gpt-4o-mini",
                    temperature: float = 1.0):
    """
    Uses the system_role and user_msg (competency descriptor) in the actual prompt.
    Properly injects all behavior-setting context.
    """
    # Combine user_msg (competency) and prompt (assignment) into a single user message
    user_content = f"{user_msg}\n\n{prompt}"

    # Add any additional structured sections (optional)
    if sections:
        for label, content in sections.items():
            user_content += f"\n\n{label}:\n{content}"

    # Send to OpenAI
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_content},
        ],
        temperature=temperature,
    )

    text = (getattr(resp, "output_text", "") or "").strip()
    return text, getattr(resp, "usage", None)


# --- Persona + Competency Prompts ---

def build_student_agent(grade_level: str, subject: str, assignment_type: str, topic: str) -> str:
    return (
        f"You are a {grade_level} student completing a {assignment_type} for your {subject} class "
        f"on the topic of '{topic}'. Write only with the skills you have. Do not overperform. "
        f"Your grammar, structure, and analysis must match your described competency. Do not write beyond your level."
    )

def competency_level(knowledge_desc: str, grammar_desc: str, flow_desc: str) -> str:
    return (
        f"Write this essay as if the student has {knowledge_desc}, uses {grammar_desc}, "
        f"and demonstrates {flow_desc}. Reflect these limitations or strengths in vocabulary, grammar, "
        f"organization, transitions, and clarity. Do not exceed the student's ability level. Let the essay reflect these competencies."
    )

# --- Essay Generator ---

def essay_gen(n, topic: str, grade_level: str, subject: str, assignment_type: str, prompt: str, model="gpt-4o-mini") -> pd.DataFrame:
    topic_clean = topic.lower().replace(" ", "_")
    student_agent = build_student_agent(grade_level, subject, assignment_type, topic)

    level_triplets = generate_level_triplets(n)
    data_rows = []

    for i, triplet in enumerate(level_triplets):
        k_desc = triplet["knowledge_desc"]
        g_desc = triplet["grammar_desc"]
        f_desc = triplet["flow_desc"]

        competency_msg = competency_level(k_desc, g_desc, f_desc)

        print(f"\n🧠 Essay {i+1}: Knowledge={triplet['knowledge_level']} ({k_desc}), "
              f"Grammar={triplet['grammar_level']} ({g_desc}), Flow={triplet['flow_level']} ({f_desc})")

        essay_text, _ = text_generation(
            system_role=student_agent,
            user_msg=competency_msg,
            prompt=prompt,
            model=model,
        )

        data_rows.append({
            "essay_id": uuid.uuid4().hex[:8],
            "title": topic.title(),
            "subject": subject,
            "grade": grade_level,
            "knowledge level": f"{triplet['knowledge_level']} - {k_desc}",
            "grammar level": f"{triplet['grammar_level']} - {g_desc}",
            "flow level": f"{triplet['flow_level']} - {f_desc}",
            "essay": essay_text
        })

    df = pd.DataFrame(data_rows)
    filename = f"essays_{topic_clean}.csv"
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"\n📄 Saved {n} essays to {filename}")
    return df

# --- Run ---
if __name__ == "__main__":
    essay_gen(
        n=1,
        topic="animal farm by George Orwell",
        grade_level="9th grade",
        subject="English",
        assignment_type="essay",
        prompt="Write an essay of 5 to 7 paragraphs according to the specified competencies."
    )
