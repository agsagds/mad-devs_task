from dataclasses import dataclass, field


@dataclass
class Chunk:
    tag: str
    pos_start: int
    pos_end: int = -1
    
    @property
    def length(self) -> int:
        return self.pos_end - self.pos_start

@dataclass
class Bracket(Chunk):
    is_start: bool = False
    
    @property
    def paired_len(self) -> int:
        return len(self.tag)*2 + 5
    
    def to_open_tag(self) -> str:
        return f'<{self.tag}>'
    
    def to_close_tag(self) -> str:
        return f'</{self.tag}>'

@dataclass
class Options:
    open_brackets: list[Bracket] = field(default_factory=list)
    header: str = ''
    cursor_pos: int = 0
    chunk_idx: int = 0
    len_close: int = 0
    len_open: int = 0
    len_open_before_pos: int = 0
    max_len: int = 0
    
    def update_lengths(self) -> None:
        self.len_close = sum((len(b.to_close_tag()) for b in self.open_brackets))
        self.len_open = sum((len(b.to_open_tag()) for b in self.open_brackets)) + len(self.header)
        self.len_open_before_pos = self.len_open - \
            sum((len(b.to_open_tag()) for b in self.open_brackets if b.pos_start >= self.cursor_pos))