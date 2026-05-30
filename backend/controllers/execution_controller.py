from backend.engines.memory_engine import (
    extract_memory,
    memory_response,
    save_context,
    get_recent_context
)

from backend.engines.retrieval_engine import (
    needs_retrieval,
    hybrid_search
)

from backend.engines.reasoning_engine import (
    generate_reasoning_response
)

from backend.engines.coding_engine import (
    generate_code_response
)

from backend.engines.vector_memory_engine import (
    store_memory,
    search_memory
)

from backend.synthesizers.response_synthesizer import (
    synthesize_response
)

# =========================
# TASK ROUTER
# =========================

def is_coding_task(prompt):

    text = prompt.lower()

    coding_actions = [

        "write",
        "build",
        "create",
        "generate",
        "make",
        "develop"
    ]

    coding_keywords = [

        "code",
        "python",
        "fastapi",
        "javascript",
        "react",
        "api",
        "backend",
        "frontend",
        "algorithm"
    ]

    has_action = any(
        word in text
        for word in coding_actions
    )

    has_code_term = any(
        word in text
        for word in coding_keywords
    )

    return has_action and has_code_term

# =========================
# EXECUTION CONTROLLER
# =========================

def execute_prompt(prompt):

    # =========================
    # STORE MEMORIES
    # =========================

    extract_memory(prompt)

    store_memory(prompt)

    # =========================
    # VECTOR MEMORY SEARCH
    # =========================

    vector_context = search_memory(prompt)

    semantic_questions = [

        "what do i use",
        "what startup",
        "which framework",
        "what framework",
        "what kind",
        "what company",
        "what laptop",
        "what language",
        "what backend"
    ]

    lowered = prompt.lower()

    # =========================
    # DIRECT SEMANTIC RECALL
    # =========================

    if vector_context and any(
        q in lowered
        for q in semantic_questions
    ):

        result = vector_context

        save_context(prompt, result)

        return synthesize_response(
            result,
            "semantic_memory"
        )

    # =========================
    # EXACT MEMORY
    # =========================

    memory_answer = memory_response(prompt)

    if memory_answer:

        save_context(prompt, memory_answer)

        return synthesize_response(
            memory_answer,
            "memory"
        )

    # =========================
    # LIVE RETRIEVAL
    # =========================

    if needs_retrieval(prompt):

        retrieval_data = hybrid_search(prompt)

        retrieval = retrieval_data["response"]

        save_context(prompt, retrieval)

        return synthesize_response(
            retrieval,
            retrieval_data["source"]
        )

    # =========================
    # CONTEXT
    # =========================

    context = get_recent_context()

    if vector_context:

        context += f"""

VECTOR MEMORY:
{vector_context}
"""

    # =========================
    # CODING TASK
    # =========================

    if is_coding_task(prompt):

        result = generate_code_response(prompt)

        save_context(prompt, result)

        return synthesize_response(
            result,
            "coding_engine"
        )

    # =========================
    # REASONING TASK
    # =========================

    result = generate_reasoning_response(
        prompt,
        context
    )

    save_context(prompt, result)

    return synthesize_response(
        result,
        "reasoning_engine"
    )