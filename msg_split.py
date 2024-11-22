from dataclasses import dataclass
from typing import Generator
from html.parser import HTMLParser

@dataclass
class Bracket:
    tag: str
    is_breakable: bool
    is_start: bool
    pos_start: int
    pos_end: int = -1
    
    @property
    def length(self):
        return self.pos_end - self.pos_start

class MyHTMLParser(HTMLParser):
    
    TAGS = { 'p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span' }
    
    def __init__(self):
        self.brackets: list[Bracket] = []
        self._custom_brackets_count = 0
        self._update_bracket_flag = False
        self.feed_offset = 0
        super().__init__()
    
    def handle_starttag(self, tag, attrs):
        self._update_bracket()
        
        if self._is_unbreackable_part:
            if self.brackets[-1].tag == tag:
                self._custom_brackets_count += 1
            return
        
        if tag in MyHTMLParser.TAGS:
            self.brackets.append(Bracket(tag, True, True, self.getpos()))
            self._update_bracket_flag = True
        else:
            self.brackets.append(Bracket(tag, False, False, self.getpos()))
            self._custom_brackets_count = 1

    def handle_endtag(self, tag):
        self._update_bracket()
        
        if self._is_unbreackable_part:
            if self.brackets[-1].tag == tag:
                self._custom_brackets_count -= 1
                
            if self._custom_brackets_count == 0:
                self._update_bracket_flag = True
            return
        
        if tag in MyHTMLParser.TAGS:
            # FIXME: can pass unpaired tag
            self.brackets.append(Bracket(tag, True, False, self.getpos()))
            self._update_bracket_flag = True
        else:
            raise Exception(f'Unpredicted closed tag {tag} at pos {self.getpos()}')
    
    def handle_data(self, data):
        self._update_bracket()
    
    def getpos(self):
        line_num, line_offset = super().getpos()
        return self.feed_offset + line_offset
    
    def _update_bracket(self):
        if self._update_bracket_flag:
            self.brackets[-1].pos_end = self.getpos()
        self._update_bracket_flag = False

    @property
    def _is_unbreackable_part(self):
        return len(self.brackets) and \
            self.brackets[-1].pos_end == -1 and (not self.brackets[-1].is_breakable)

    

MAX_LEN = 4096

# def split_message(source: str, max_len=MAX_LEN) -> Generator[str]:
#     """Splits the original message (`source`) into fragments of the specified length(`max_len`).

#     Args:
#         source (str): Source html message
#         max_len (int, optional): Max lenght of message part. Defaults to MAX_LEN.

#     Yields:
#         Generator[str]: Return next part of message
#     """
    
#     # 1 - convert to bracket sequence
#     # 2 - make greedy online solution
#     yield '123'