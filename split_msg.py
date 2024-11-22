from msg_split import MyHTMLParser, Bracket
import pprint

if __name__ == '__main__':
    
    max_len = 20
    
    parser = MyHTMLParser()
    text = ''
    with open('/home/locus/workspace/test-tasks/mad-devs/mad-devs_task/data/simple.html') as f:
        for line in f.readlines():
            parser.feed(line)
            parser.feed_offset += len(line)+1
            text += line + '\n'
    pprint.pprint(
        [(b, text[b.pos_start: b.pos_end]) for b in parser.brackets]
        )

    bs = parser.brackets
    open_bs: list[Bracket] = []
    pos = 0
    i = 0
    while pos < len(text):
        len_close = sum((len(b.tag)+3 for b in open_bs))
        len_open = len_close - len(open_bs)
        
        if bs[i].length > max_len:
            raise Exception(f'Unsplitted block at pos {bs[i].pos_start} with length {bs[i].length} greater than max_len {max_len}')

        if (not bs[i].is_start) and bs[i].tag == open_bs[-1].tag:
            open_bs.pop()
            i+=1
            continue
        
        if bs[i].is_start:
            if len(bs[i].tag)*2+5 + bs[i].pos_start - pos > max_len:
                if len(bs[i].tag) + len_close + len_open < max_len:
                    break_line
                    continue
                raise Exception(f'Length of pure hierarchy of open-closed tags greater than max_len {max_len}')
            open_bs.append(bs[i])
            i+=1
            continue
        
        if (not bs[i].is_breakable) and bs[i].pos_end - pos + len_close > max_len:
            if bs[i-1].pos_end - pos + len_close > max_len:
                raise Exception(f'Cannot split part of text from pos {pos}')
            pos_end = min(pos + max_len - len_close, bs[i].pos_start)
            part = text[pos:pos_end] + ''.join((f'</{b.tag}>' for b in open_bs))
            pos = pos_end
        
        
        

        