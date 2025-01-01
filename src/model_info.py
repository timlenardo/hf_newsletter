from urllib.parse import quote_plus

from web_search import web_read

def get_model_description(model_id, fallback_description=""):
    """Search the web for information about a model and create a brief description."""
    try:
        # First try searching directly for the model
        search_query = f"https://www.google.com/search?q={quote_plus(f'huggingface {model_id} AI model what is it')}"
        search_results = web_read(url=search_query)
        
        if not search_results or len(search_results) < 100:
            # If first search didn't yield good results, try a broader search
            model_name = model_id.split('/')[-1]
            search_query = f"https://www.google.com/search?q={quote_plus(f'{model_name} AI model capabilities')}"
            search_results = web_read(url=search_query)
        
        if search_results and len(search_results) > 100:
            # Extract relevant information from search results
            # Remove common noise from search results
            clean_results = search_results.replace("Search Results", "")
            clean_results = clean_results.split("More items...")[0]
            
            # Get the first few sentences that mention the model or relevant terms
            sentences = clean_results.split('.')
            relevant_sentences = []
            model_terms = set(model_id.lower().replace('/', ' ').split())
            
            for sentence in sentences[:10]:  # Look at first 10 sentences
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Check if sentence is relevant
                sentence_lower = sentence.lower()
                if (any(term in sentence_lower for term in model_terms) or
                    any(term in sentence_lower for term in ['model', 'ai', 'neural', 'trained', 'designed'])):
                    relevant_sentences.append(sentence)
                
                if len(relevant_sentences) >= 2:  # Get at least 2 relevant sentences
                    break
            
            if relevant_sentences:
                description = '. '.join(relevant_sentences)
                # Clean up the description
                description = description.replace('...', '.')
                description = description.strip()
                if not description.endswith('.'):
                    description += '.'
                return description
    
    except Exception as e:
        print(f"Error getting description for {model_id}: {str(e)}")
    
    return fallback_description or "No description available"