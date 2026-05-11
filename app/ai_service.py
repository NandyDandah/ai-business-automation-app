def analyse_business_message(message: str):
    lower = message.lower()

    category = "admin"
    priority = "medium"
    score = 30

    if "price" in lower or "pricing" in lower or "quote" in lower or "cost" in lower:
        category = "sales"
        score += 30

    if "complaint" in lower or "unhappy" in lower or "refund" in lower or "bad service" in lower:
        category = "complaint"
        priority = "high"
        score += 20

    if "help" in lower or "support" in lower or "problem" in lower or "issue" in lower:
        category = "support"
        score += 15

    if "follow up" in lower or "checking in" in lower:
        category = "follow_up"
        score += 10

    if "urgent" in lower or "asap" in lower:
        priority = "high"
        score += 20

    if score >= 70:
        priority = "high"

    score = min(score, 100)

    return {
        "category": category,
        "priority": priority,
        "reply": f"Thank you for your message. We have categorized your request as {category}. Our team will respond shortly.",
        "lead_score": score
    }