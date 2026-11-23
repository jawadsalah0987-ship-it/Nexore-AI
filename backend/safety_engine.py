# safety_engine.py

def analyze_safety(detections):
    """
    Nexora AI - Safety Analysis Engine
    Analyzes detected objects and explicit PPE violations.
    """

    if not isinstance(detections, list):
        detections = []

    # Normalize class names
    detected_items = []

    for item in detections:
        name = str(item.get("object", "")).lower().strip()
        confidence = float(item.get("confidence", 0))

        detected_items.append({
            "name": name.replace("_", " ").replace("-", " "),
            "confidence": confidence
        })

    # Class groups
    person_labels = {"person", "worker", "employee"}

    helmet_labels = {
        "helmet", "hardhat", "hard hat", "safety helmet"
    }

    vest_labels = {
        "vest", "safety vest", "reflective vest", "high visibility vest"
    }

    negative_helmet_labels = {
        "no helmet", "no hardhat", "no hard hat",
        "without helmet", "missing helmet"
    }

    negative_vest_labels = {
        "no vest", "no safety vest",
        "without vest", "missing vest"
    }

    # Count detected categories
    people = [
        x for x in detected_items
        if x["name"] in person_labels
    ]

    helmets = [
        x for x in detected_items
        if x["name"] in helmet_labels
    ]

    vests = [
        x for x in detected_items
        if x["name"] in vest_labels
    ]

    missing_helmets = [
        x for x in detected_items
        if x["name"] in negative_helmet_labels
        and x["confidence"] >= 0.45
    ]

    missing_vests = [
        x for x in detected_items
        if x["name"] in negative_vest_labels
        and x["confidence"] >= 0.45
    ]

    # Risk analysis
    risks = []

    for item in missing_helmets:
        risks.append({
            "type": "Missing Helmet",
            "severity": "Critical",
            "confidence": item["confidence"],
            "message": "Possible missing helmet detected."
        })

    for item in missing_vests:
        risks.append({
            "type": "Missing Safety Vest",
            "severity": "High",
            "confidence": item["confidence"],
            "message": "Possible missing safety vest detected."
        })

    if missing_helmets:
        risk_level = "Critical"
        safety_status = "Unsafe"

    elif missing_vests:
        risk_level = "High"
        safety_status = "Unsafe"

    elif not people:
        risk_level = "Unknown"
        safety_status = "Needs Review"

    else:
        risk_level = "Unverified"
        safety_status = "Needs Review"

    # Summary
    summary = {
        "people_detected": len(people),
        "helmets_detected": len(helmets),
        "vests_detected": len(vests),
        "missing_helmets_detected": len(missing_helmets),
        "missing_vests_detected": len(missing_vests),
        "risk_level": risk_level,
        "safety_status": safety_status,
        "risks": risks,
        "message": (
            "Safety violations detected."
            if risks
            else "No explicit PPE violation was detected. "
                 "This does not confirm full safety compliance."
        )
    }

    return summary