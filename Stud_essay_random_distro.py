import random
import os
from openai import OpenAI
from dotenv import load_dotenv

# --- Environment Setup ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ OpenAI API key is loaded!")
else:
    print("❌ OpenAI API key NOT loaded.")

client = OpenAI()

# --- Knowledge and Grammar Scales ---

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
    1: "poor flow and organization. There no thesis",
    2: "weak flow with some organization issues, the thesis is unclear",
    3: "adequate flow and organization,the theis is in the first paragraph and the conclusion is in the last ",
    4: "good flow and well-organized.The thesis is clear and the conclusion summarizes the main points. The ideas flow logically from paragraph to paragraph",
    5: "excellent flow and highly organized. The thesis is compelling and well-placed, and the conclusion effectively reinforces the main arguments. Transitions between paragraphs are smooth and enhance readability."
}
# --- Sampling Functions ---

def sample_knowledge(n):
    """
    Returns a list of knowledge levels (1–5) using a normal distribution.
    Centered at 3.5 with sigma=1 → most values around 3–4.
    """
    samples = []
    for _ in range(n):
        level = round(random.gauss(mu=3.5, sigma=1))
        level = max(1, min(5, level))  # Clamp to 1–5
        samples.append(level)
    return samples

def sample_grammar_from_knowledge(knowledge_level):
    """
    Returns a grammar level based on knowledge level ±1 (clamped between 1 and 5).
    Simulates correlation between knowledge and grammar.
    """
    delta = random.choice([-1, 0, 1])
    grammar_level = max(1, min(5, knowledge_level + delta))
    return grammar_level

def sample_flow_from_knowledge(knowledge_level):
    """
    Returns a flow level based on knowledge level ±1 (clamped between 1 and 5).
    Simulates correlation between knowledge and flow.
    """
    delta = random.choice([-1, 0, 1])
    flow_level = max(1, min(5, knowledge_level + delta))
    return flow_level


def generate_level_pairs(n):
    """
    Generate n (knowledge, grammar) level pairs using bell-curve for knowledge
    and ±1 rule for grammar.
    """
    triplet = []
    knowledge_samples = sample_knowledge(n)
    for k in knowledge_samples:
        g = sample_grammar_from_knowledge(k)
        f = sample_flow_from_knowledge(k)
        triplet.append({
            "knowledge_level": k,
            "knowledge_desc": knowledge_levels[k],
            "grammar_level": g,
            "grammar_desc": grammar_levels[g],
            "flow_level": f,
            "flow_desc": flow_levels[f]

        })
    return triplet

# --- OpenAI Text Generation ---

def text_generation(system_role: str, user_msg: str, prompt: str, sections: dict | None = None,
                    model: str = "gpt-4o-mini", temperature: float = 1.0):
    """
    Wrapper for OpenAI text generation using the Responses API.
    """
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

# --- Persona Building ---

def build_student_agent(grade_level: str, subject: str, assignment_type: str, topic: str) -> str:
    """
    Builds a student persona for the essay generation context.
    """
    return f"You are a {grade_level} student completing a {assignment_type} for your {subject} class on the topic of '{topic}'. 5% of the times, you will put the thesis not in the first paragrah."

def competency_level(knowledge_desc: str, grammar_desc: str) -> str:
    """
    Combine knowledge and grammar descriptors into a single student competency description.
    """
    return f"You demonstrate {knowledge_desc}, and your writing shows {grammar_desc}."

# --- Essay Generation Pipeline ---

def essay_gen(n, topic: str, grade_level: str, subject: str, assignment_type: str, prompt: str, model="gpt-4o-mini"):
    """
    Generates n essays using randomized competency levels (knowledge + grammar)
    distributed according to a normal curve.
    """
    topic_clean = topic.lower().replace(" ", "_")
    student_agent = build_student_agent(grade_level, subject, assignment_type, topic)

    # Generate correlated knowledge/grammar pairs
    level_pairs = generate_level_pairs(n)

    essay_vars = []

    for i, pair in enumerate(level_pairs):
        k_desc = pair["knowledge_desc"]
        g_desc = pair["grammar_desc"]
        student_competency = competency_level(k_desc, g_desc)

        print(f"🧠 Essay {i+1}: Knowledge={pair['knowledge_level']} ({k_desc}), Grammar={pair['grammar_level']} ({g_desc})")

        essay_text, _ = text_generation(
            system_role=student_agent,
            user_msg=student_competency,
            prompt=prompt,
            model=model,
        )
        var_name = f"essay_{topic_clean}_{i}"
        essay_vars.append((var_name, essay_text))

    # Save essays to a file
    filename = f"essays_{topic_clean}.py"
    with open(filename, "w", encoding="utf-8") as f:
        for var_name, essay_text in essay_vars:
            f.write(f'{var_name} = """{essay_text}"""\n\n')

    print(f"✅ Saved {n} essays to {filename}")

# --- Example Usage ---
if __name__ == "__main__":
    essay_gen(
        n=6,
        topic="The Great Gatsby",
        grade_level="10th grade",
        subject="English",
        assignment_type="essay",
        prompt="Write an essay of 5 to 7 paragraphs with an introduction, thesis, and conclusion. Discuss themes, character development, and symbolism."
    )



###Add flow vector to ard code. 
# add knowledge, flow, grammar, grade, topic to title of essays""