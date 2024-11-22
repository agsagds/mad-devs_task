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
