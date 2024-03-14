from argparse import ArgumentParser
from . import wormgrok as wgrok

MODE_SEND = 'send'
MODE_RECEIVE = 'receive'

parser = ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

parser_send = subparsers.add_parser(MODE_SEND)
parser_receive = subparsers.add_parser(MODE_RECEIVE)

parser_send.add_argument('--file-path')
parser_send.add_argument('--file-name')
parser_receive.add_argument('--dest-dir')

args = parser.parse_args()

if args.command == MODE_SEND:
    operation = wgrok.send_file(args.file_path, args.file_name)

    with operation as (loop, public_url):
        print("Download URL:", public_url)
        print("Download URL:", public_url + '/' + args.file_name)
        loop.run_forever()

elif args.command == MODE_RECEIVE:
    operation = wgrok.receive_file(args.dest_dir)

    with operation as (loop, public_url):
        print("Public URL:", public_url)

        print()
        print("Need to send a file from a terminal? On the other computer, run the following cURL command:")
        print(f"curl -X POST \"{public_url}/<filename>\" --data-binary @<local_file_path>")
        
        loop.run_forever()

else:
    exit(1)


