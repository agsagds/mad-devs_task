import argparse
from msg_split import split_message
from msg_split.const import MAX_LEN




if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
                    prog='HTML Fragmentation',
                    description='Fragmentate HTML to correct HTML chunks')
    parser.add_argument('--max-length', dest='max_len', required=True, type=int)
    parser.add_argument('filepath', type=str)

    args = parser.parse_args()
    with open(args.filepath) as f:
        text = f.read()
        fragment_num = 1
        for fragment in split_message(text, args.max_len):
            print(f'fragment #{fragment_num}: {len(fragment)} chars.')
            print(fragment)
            fragment_num+=1
    