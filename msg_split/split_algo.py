from collections.abc import Generator
from operator import attrgetter
from .const import MAX_LEN
from .models import Bracket, Chunk, Options
from .parser import MyHTMLParser
from .exceptions import ParseError, SplitError

def _break_source(opts: Options, pos_end: int, source: str) -> tuple[str, int]:
    header_brackets = opts.closed_brackets + \
        [b for b in opts.open_brackets if b.pos_start < opts.cursor_pos]
    header_brackets.sort(key=attrgetter('pos_start'))
    header = ''.join([b.to_open_tag() for b in header_brackets])
    footer = ''.join([b.to_close_tag() for b in opts.open_brackets[::-1]])
    
    pos_end = min(opts.cursor_pos + (opts.max_len - len(header)-len(footer)), pos_end)
    body = source[opts.cursor_pos:pos_end]
    source_part = header + body + footer
    
    return source_part, pos_end

def _parse_chunks(source: str) -> list[Chunk | Bracket]:
    parser = MyHTMLParser()
    for line in source.split('\n'):
        parser.feed(line+'\n')
        parser.feed_offset += len(line)+1
    return parser.chunks

def _check_chunk_length(chunk: Chunk, opts: Options, source: str) -> None:
    if chunk.length > opts.max_len:
        raise SplitError(f'Unsplitted block at pos {chunk.pos_start} with length'
                        f' {chunk.length} greater than max_len {opts.max_len}',
                        source[chunk.pos_start:chunk.pos_end])

def _process_open_bracket(br: Bracket, opts: Options, source: str) ->  str | None:
    full_len_with_tag = br.paired_len + opts.len_open_before_pos + opts.len_close + br.pos_start - opts.cursor_pos
    pure_len_with_tag = br.paired_len + opts.len_close + opts.len_open
    
    if full_len_with_tag > opts.max_len:
        if pure_len_with_tag > opts.max_len:
            raise SplitError('Length of pure hierarchy of open-closed tags'
                        f'greater than max_len {opts.max_len}')
        part, opts.cursor_pos = _break_source(opts, br.pos_start, source)
        opts.closed_brackets.clear()
        return part
        
    opts.open_brackets.append(br)
    opts.chunk_idx += 1
    return None

def _process_close_bracket(br: Bracket, opts: Options, source: str) ->  str | None:
    if len(opts.open_brackets) == 0 or br.tag != opts.open_brackets[-1].tag:
        raise ParseError(f'Upaired tag `{br.tag}` in pos {br.pos_start}')
    
    full_len = opts.len_open_before_pos + opts.len_close + br.pos_start - opts.cursor_pos
    
    if full_len > opts.max_len:
        part, opts.cursor_pos = _break_source(opts, br.pos_start, source)
        opts.closed_brackets.clear()
        return part
    
    bracket = opts.open_brackets.pop()
    if bracket.pos_start < opts.cursor_pos:
        opts.closed_brackets.append(bracket)
    opts.chunk_idx+=1
    return None

def _process_unbreakable_chunk(chunk: Chunk, opts: Options, source: str) ->  str | None:
    full_len_with_chunk = chunk.pos_end - opts.cursor_pos + opts.len_close + opts.len_open_before_pos
    pure_len_with_chunk = chunk.length + opts.len_open + opts.len_close
    
    if full_len_with_chunk > opts.max_len:
        if pure_len_with_chunk > opts.max_len:
            raise SplitError('Length of pure hierarchy of open-closed tags'
                            f'and unbreakable part from pos {chunk.pos_start}'
                            f'greater than max_len {opts.max_len}')
        part, opts.cursor_pos = _break_source(opts, chunk.pos_start, source)
        opts.closed_brackets.clear()
        return part

    opts.chunk_idx += 1
    return None

def split_message(source: str, max_len=MAX_LEN) -> Generator[str]:
    """Splits the original message (`source`) into fragments of the specified length(`max_len`).

    Args:
        source (str): Source html message
        max_len (int, optional): Max lenght of message fragment. Defaults to MAX_LEN.

    Yields:
        Generator[str]: Return next fragment of message
    """
    
    # 1 - convert to bracket sequence
    chunks = _parse_chunks(source)
    
    # 2 - make greedy online solution
    opts: Options = Options(max_len=max_len)
    
    while opts.chunk_idx < len(chunks): # go through brackets
        result = None
        opts.update_lengths()
        
        _check_chunk_length(chunks[opts.chunk_idx], opts, source)
        
        if isinstance(chunks[opts.chunk_idx], Bracket):
            if chunks[opts.chunk_idx].is_start:
                result =_process_open_bracket(chunks[opts.chunk_idx], opts, source)
            else:
                result =_process_close_bracket(chunks[opts.chunk_idx], opts, source)
        else:
            result = _process_unbreakable_chunk(chunks[opts.chunk_idx], opts, source)
        
        if result is not None:
            yield result
    
    if len(opts.open_brackets) > 0: 
        raise ParseError(f'Unpaired open tag `{opts.open_brackets[0].tag}` at pos'
                        f'{opts.open_brackets[0].pos_start}')
    
    # just send tail without special rules
    while opts.cursor_pos < len(source):
        part, opts.cursor_pos = _break_source(opts, len(source), source)
        opts.closed_brackets.clear()
        if len(part.strip(' \n')): # we don't need to return empty tail
            yield part
