from typing import Generator


MAX_LEN = 4096
TAGS = { 'p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span' }

def split_message(source: str, max_len=MAX_LEN) -> Generator[str]:
    """Splits the original message (`source`) into fragments of the specified length(`max_len`).

    Args:
        source (str): Source html message
        max_len (int, optional): Max lenght of message part. Defaults to MAX_LEN.

    Yields:
        Generator[str]: Return next part of message
    """
    
    # 1 - convert to bracket sequence
    # 2 - make greedy online solution