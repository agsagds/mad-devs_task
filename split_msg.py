from msg_split import split_message
import pprint

fragment_num = 1

if __name__ == '__main__':
    
    max_len = 4296
    with open('/home/locus/workspace/test-tasks/mad-devs/mad-devs_task/data/source.html') as f:
        text = f.read()
        for fragment in split_message(text, max_len):
            print(f'fragment #{fragment_num}: {len(fragment)} chars.')
            print(fragment[:50], '\n...\n', fragment[-50:])
            fragment_num+=1
    