import openai
from models import SuggestedWord, Word, Toddler

# Initialize OpenAI API
openai.api_key = "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"

def get_word_suggestion(category, user_id):
    # Get toddler associated with the user
    toddler = Toddler.query.filter_by(user_id=user_id).first()

    # If there's no toddler associated with this user, return None
    if not toddler:
        return None

    # Prepare the prompt for OpenAI
    age_in_months = toddler.age  # Assuming 'age' in the Toddler model is represented in months
    prompt = f"Provide a single word related to {category} that is suitable for a {age_in_months} month old toddler. Only repsond with the one single word. For example, the response should look like this 'Animal'"

    response = openai.Completion.create(engine="text-davinci-003",prompt=prompt, max_tokens=60
)
    
    print(response)
    word_string = response.choices[0].text.strip()

    # Search for the word in the Word table
    word_instance = Word.query.filter_by(word=word_string).first()

    if word_instance:
        # If the word exists in the Word table, check if it has been suggested for the toddler
        suggested_word = SuggestedWord.query.filter_by(word_id=word_instance.id, toddler_id=toddler.id).first()
        
        # If it hasn't been suggested before, then suggest it
        if not suggested_word:
            return word_string
        else:
            # Handle the case where the word has already been suggested for this toddler
            return None
    else:
        # If the word doesn't exist in the Word table, suggest it
        return word_string

