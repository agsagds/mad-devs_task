from dataclasses import dataclass
from collections.abc import Generator
from html.parser import HTMLParser

class ParseError(Exception):
    pass

class SplitError(Exception):
    pass

class TagConvertError(Exception):
    pass

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
    
    @property
    def paired_len(self):
        if not self.is_breakable:
            raise TagConvertError(f'Trying to calc paired len for unbreakable tag `{self.tag}`')
        return len(self.tag)*2 + 5
    
    def to_open_tag(self):
        if not self.is_breakable:
            raise TagConvertError(f'Trying to convert unbreakable tag `{self.tag}`')
        return f'<{self.tag}>'
    
    def to_close_tag(self):
        if not self.is_breakable:
            raise TagConvertError(f'Trying to convert unbreakable tag `{self.tag}`')
        return f'</{self.tag}>'

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
            raise ParseError(f'Unpredicted closed tag `{tag}` at pos {self.getpos()}')
    
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

def _break_text(pos_start: int, pos_end: int, open_bs: list[Bracket], header: str, text: str, max_len: int) -> tuple[str, int]:

    header += ''.join([b.to_open_tag() for b in open_bs if b.pos_start < pos_start])
    footer = ''.join([b.to_close_tag() for b in open_bs[::-1]])
    
    pos_end = min(pos_start + (max_len - len(header)-len(footer)), pos_end)
    body = text[pos_start:pos_end]
    text_part = header + body + footer
    
    return text_part, pos_end    

MAX_LEN = 4096

def split_message(source: str, max_len=MAX_LEN) -> Generator[str]:
    """Splits the original message (`source`) into fragments of the specified length(`max_len`).

    Args:
        source (str): Source html message
        max_len (int, optional): Max lenght of message part. Defaults to MAX_LEN.

    Yields:
        Generator[str]: Return next part of message
    """
    
    # 1 - convert to bracket sequence
    parser = MyHTMLParser()
    for line in source.split('\n'):
        parser.feed(line+'\n')
        parser.feed_offset += len(line)+1
    # import pprint
    # pprint.pprint([(b, source[b.pos_start: b.pos_end]) for b in parser.brackets])
    bs = parser.brackets
    
    # 2 - make greedy online solution
    open_bs: list[Bracket] = []
    header = ''
    pos = 0
    i = 0
    
    while i < len(bs):
        len_close = sum((len(b.to_close_tag()) for b in open_bs))
        len_open = sum((len(b.to_open_tag()) for b in open_bs)) + len(header)
        len_open_before_pos = len_open - \
            sum((len(b.to_open_tag()) for b in open_bs if b.pos_start >= pos))
        
        if bs[i].length > max_len:
            raise SplitError(f'Unsplitted block at pos {bs[i].pos_start} with length'
                            f' {bs[i].length} greater than max_len {max_len}',
                            source[bs[i].pos_start:bs[i].pos_end])
        
        if bs[i].is_start:
            if bs[i].paired_len + len_open_before_pos + bs[i].pos_start - pos > max_len:
                if bs[i].paired_len + len_close + len_open < max_len:
                    part, pos = _break_text(pos, bs[i].pos_start, open_bs, header, source, max_len)
                    header = ''
                    yield part
                    continue
                raise SplitError('Length of pure hierarchy of open-closed tags'
                                f'greater than max_len {max_len}')
            open_bs.append(bs[i])
            i+=1
        else:
            if len(open_bs) and bs[i].tag == open_bs[-1].tag:
                bracket = open_bs.pop()
                if bracket.pos_start < pos:
                    header = bracket.to_open_tag() + header
                i+=1
                continue
        
            if not bs[i].is_breakable:
                if bs[i].pos_end - pos + len_close + len_open_before_pos > max_len:
                    if bs[i].length + len_open + len_close > max_len:
                        raise SplitError('Length of pure hierarchy of open-closed tags'
                                        f'and unbreakable part from pos {bs[i].pos_start}'
                                        f'greater than max_len {max_len}')
                    part, pos = _break_text(pos, bs[i].pos_start, open_bs, header, source, max_len)
                    header = ''
                    yield part
                    continue
                i+=1
            else:
                raise ParseError(f'Upaired tag `{bs[i].tag}` in pos {bs[i].pos_start}')
    
    if len(open_bs) > 0:
            raise ParseError(f'Unpaired open tag `{open_bs[0].tag}` at pos'
                            f'{open_bs[0].pos_start}')
            
    while pos < len(source):
        part, pos = _break_text(pos, len(source), open_bs, header, source, max_len)
        header = ''
        if len(part.strip(' \n')):
            yield part
