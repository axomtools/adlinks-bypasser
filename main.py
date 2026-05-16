import sys
import argparse
from bypasser import bypassadlink, getfinalcontent

def main():
    parser = argparse.ArgumentParser(description='Ultimate adlink bypasser')
    parser.add_argument('url', help='Adlink URL')
    parser.add_argument('--content', action='store_true', help='Get final page content')
    parser.add_argument('--headless', action='store_true', help='Run browser headless')
    args = parser.parse_args()
    if args.headless:
        import config
        config.headless = True
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
            print('Failed to bypass', file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
