def compute_confidence(similarity_scores: list) -> int: 
    if not similarity_scores:
        return 0
    MAX_DISTANCE = 2.0 
    similarities= [max(0, 1 - (score/MAX_DISTANCE)) for score in similarity_scores]
    if len(similarities) == 1: 
        weighted = similarities[0]
    elif len(similarities) ==2:
        weighted = similarities[0] * 0.6 + similarities[1] * 0.4
    else: 
        rest_avg =sum(similarities[1:]) / len(similarities[1:])
        weighted = similarities[0] * 0.6 + rest_avg * 0.4
    return int(weighted * 100) 

def confidence_label(score:int) -> tuple: 
    if score >= 75:
        return('High Confidence', '#27AE60')
    elif score >= 50: 
        return('Medium Confidence', '#F39C12')
    else:
        return ('Low Confidence --> HR Notified', '#E74C3C')
    
    
