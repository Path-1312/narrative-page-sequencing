def extract_head_tail(text, num_words=60):
    """
    Extracts the first and last N words of a page to represent its 'edges'.
    """
    words = str(text).split()
    # If the page is shorter than 2*num_words, just split it in half
    if len(words) < num_words * 2:
        mid = len(words) // 2
        return " ".join(words[:mid]), " ".join(words[mid:])
    
    head = " ".join(words[:num_words])
    tail = " ".join(words[-num_words:])
    return head, tail