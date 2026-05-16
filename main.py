import sys
import argparse
from bypasser import bypassadlink, getfinalcontent

def main():
    parser = argparse.ArgumentParser(description='Get content from adlinks')
    parser.add_argument('url', help='Adlink URL')
    parser.add_argument('--content', action='store_true', help='Get full content of final URL')
    args = parser.parse_args()
    if args.content:
        content = getfinalcontent(args.url)
        if content:
            print(content)
        else:
            print('Failed to get content', file=sys.stderr)
            sys.exit(1)
    else:
        result = bypassadlink(args.url)
        if result:
            print(result)
        else:
            print('Failed to bypass adlink', file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
