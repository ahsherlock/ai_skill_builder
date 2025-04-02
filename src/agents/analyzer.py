def quiz_analyzer_agent(skills, quiz_responses, questions):
    total_points_possible = sum(q[3] for q in questions)
    points_earned = 0
    skill_scores = {skill: {"points": 0, "possible": 0} for skill in skills}
    
    for question, skill, correct_answer, points, _ in questions:
        user_answer = quiz_responses.get(question, "").strip().lower()
        correct_answer = correct_answer.lower()
        
        if user_answer == correct_answer:
            points_earned += points
            skill_scores[skill]["points"] += points
        elif correct_answer in user_answer:
            partial_points = points // 2
            points_earned += partial_points
            skill_scores[skill]["points"] += partial_points
        
        skill_scores[skill]["possible"] += points
    
    proficiency = {skill: (scores["points"] / scores["possible"] * 100) if scores["possible"] > 0 else 100 
                   for skill, scores in skill_scores.items()}
    
    skill_gaps = [(skill, proficiency[skill]) for skill in skills if proficiency[skill] < 70]
    skill_gaps.sort(key=lambda x: x[1])
    prioritized_gaps = [gap[0] for gap in skill_gaps] if skill_gaps else ["No significant gaps detected"]
    
    return {
        "total_score": (points_earned / total_points_possible * 100) if total_points_possible > 0 else 100,
        "proficiency": proficiency,
        "gaps": prioritized_gaps
    }