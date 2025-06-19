import sys
import os
import json
# Ajout du répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.tools.feedback_analyzer import analyze_feedback

def run_test():
    # Charger les feedbacks
    feedbacks_path = os.path.join(os.path.dirname(__file__), '../backend/data/feedbacks.json')
    with open(feedbacks_path, 'r', encoding='utf-8') as f:
        feedbacks = json.load(f)
    
    # Concaténer les feedbacks avec le séparateur
    feedbacks_str = '\n---\n'.join(feedbacks)
    print("\nFeedbacks envoyés à analyze_feedback :\n" + feedbacks_str + "\n")
    
    try:
        result = analyze_feedback(feedbacks_str)
        print("\nRésultat structuré :\n" + json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nErreur lors de l'appel à analyze_feedback : {e}")

if __name__ == "__main__":
    run_test() 