import spacy


nlp = spacy.load("en_core_web_sm")


def split_text_into_sentence_groups(text: str) -> list:
    """
    This function splits a given text string into groups of sentences,
    ensuring each group contains a maximum of 20 sentences.

    Args:
        text (str): The text string to be split.

    Returns:
        list: A list containing the text split into groups of sentences,
              where each group has no more than 20 sentences.
    """
    doc = nlp(text)
    sentence_groups = []
    current_group = []

    for sent in doc.sents:
        current_group.append(sent.text)
        if len(current_group) == 20:
            current_group = " ".join(current_group)
            sentence_groups.append(current_group)
            current_group = []

    if current_group:
        current_group = " ".join(current_group)
        sentence_groups.append(current_group)

    return sentence_groups
