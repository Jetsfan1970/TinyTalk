import openai
from models import SuggestedWord, Word, Toddler

# Initialize OpenAI API
openai.api_key = "test"

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
        suggested_word = SuggestedWord.query.filter_by(word_id=word_instance.id, toddler_id=toddler.id).first()

        if not suggested_word:
            # Return a tuple with the word and a flag indicating it doesn't exist
            return word_string, False
        else:
            # Return a tuple with the word and a flag indicating it exists
            return word_string, True
    else:
        # Return a tuple with the word and a flag indicating it doesn't exist
        return word_string, False

