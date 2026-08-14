
def recommendation(mastery):
    if mastery < 40: return "Foundation Guide"
    if mastery < 60: return "Guided Practice"
    if mastery < 75: return "Standard Practice"
    if mastery < 90: return "Advanced Practice"
    return "Elite Challenge"
