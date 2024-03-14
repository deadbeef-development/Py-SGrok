import os

from aiohttp.client import ClientSession

from ...wormgrok import receive_file

test_dest_dir = 'test_received_files'

test_receive_file_content = b"Hello world!"
test_receive_file_path = test_dest_dir + '/psa.txt'
test_receive_file_name = "psa.txt"

async def run_test_client(public_url: str):
    async with ClientSession() as session:
        async with session.post(public_url + '/' + test_receive_file_name, data=test_receive_file_content) as response:
            response.raise_for_status()
        
        with open(test_receive_file_path, 'rb') as fio:
            received_content = fio.read()
        
        assert received_content == test_receive_file_content

        print("SUCCESS!")

if not os.path.exists(test_dest_dir):
    os.makedirs(test_dest_dir)

with receive_file(test_dest_dir) as (loop, public_url):
    print(f"Public URL: {public_url}")
    loop.run_until_complete(run_test_client(public_url))



