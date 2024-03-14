from aiohttp.client import ClientSession

from ...wormgrok import send_file

test_send_file_content = b"Hello world!"
test_send_file_path = "test_send_file.txt"
test_send_file_name = "psa.txt"

with open(test_send_file_path, 'wb') as fio:
    fio.write(test_send_file_content)

async def run_test_client(public_url: str):
    async with ClientSession() as session:
        async with session.get(public_url + '/' + test_send_file_name) as response:
            data = await response.read()
            assert data == test_send_file_content
            print("SUCCESS!")

with send_file(test_send_file_path, test_send_file_name) as (loop, public_url):
    print(f"Public URL: {public_url}")
    loop.run_until_complete(run_test_client(public_url))

