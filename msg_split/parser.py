from html.parser import HTMLParser
from .const import TAGS
from .models import Chunk, Bracket
from .exceptions import ParseError

class MyHTMLParser(HTMLParser):
    
    def __init__(self):
        self.chunks: list[Chunk | Bracket] = []
        self._chunks_hierarhy_height = 0
        self._update_pos_flag = False
        self.feed_offset = 0
        super().__init__()
    
    def handle_starttag(self, tag, attrs):
        self._update_chunk()
        
        if self._is_unbreackable_chunk:
            if self.chunks[-1].tag == tag:
                self._chunks_hierarhy_height += 1
            return
        
        if tag in TAGS:
            self.chunks.append(Bracket(tag=tag, is_start=True, pos_start=self.getpos()))
            self._update_pos_flag = True
        else:
            self.chunks.append(Chunk(tag=tag, pos_start=self.getpos()))
            self._chunks_hierarhy_height = 1

    def handle_endtag(self, tag):
        self._update_chunk()
        
        if self._is_unbreackable_chunk:
            if self.chunks[-1].tag == tag:
                self._chunks_hierarhy_height -= 1
                
            if self._chunks_hierarhy_height == 0:
                self._update_pos_flag = True
            return
        
        if tag in TAGS:
            self.chunks.append(Bracket(tag=tag, is_start=False, pos_start=self.getpos()))
            self._update_pos_flag = True
        else:
            raise ParseError(f'Unpredicted closed tag `{tag}` at pos {self.getpos()}')
    
    def handle_data(self, data):
        self._update_chunk()
    
    def getpos(self):
        line_num, line_offset = super().getpos()
        return self.feed_offset + line_offset
    
    def _update_chunk(self):
        if self._update_pos_flag:
            self.chunks[-1].pos_end = self.getpos()
        self._update_pos_flag = False

    @property
    def _is_unbreackable_chunk(self):
        return len(self.chunks) and \
            self.chunks[-1].pos_end == -1 and (not isinstance(self.chunks[-1], Bracket))
