from contextlib import contextmanager
import asyncio
import os

import ngrok
from aiohttp import web as aioweb

INDEX_HTML_CONTENT = \
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Upload</title>
    <script>
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            const fileName = file.name;

            if (!file) {
                alert('Please select a file.');
                return;
            }

            try {
                const response = await fetch('/' + encodeURIComponent(fileName), {
                    method: 'POST',
                    body: file // This sends the file as raw binary content.
                });

                if (response.ok) {
                    alert('File uploaded successfully.');
                } else {
                    alert('File upload failed.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while uploading the file.');
            }
        }
    </script>
</head>
<body>
    <h1>Upload a File</h1>
    <input type="file" id="fileInput">
    <button onclick="uploadFile()">Upload</button>
</body>
</html>

"""

@contextmanager
def _expose_ngrok(port: int):
    url = ngrok.forward(port, authtoken_from_env=True).url()

    try:
        yield url
    finally:
        ngrok.disconnect(url)

@contextmanager
def _run_http_server(app: aioweb.Application):
    handler = app.make_handler()

    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(handler, '127.0.0.1', 0)
    server = loop.run_until_complete(coroutine)
    
    host, port = server.sockets[0].getsockname()
    port: int

    try:
        yield loop, port
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())

async def _aio_input(prompt: str):
    return await asyncio.to_thread(input, prompt)

async def _ask_user_yes_or_no(default_answer = False) -> bool:
    default_answer_str = 'Y' if default_answer else 'N'
    answer = (await _aio_input(f"Enter \"Y\" or \"N\" (Default: {default_answer_str}) > ")).lower()

    if answer == 'y':
        return True
    elif answer == 'n':
        return False
    elif answer == '':
        return default_answer
    else:
        return False

async def _index(request: aioweb.Request):
    return aioweb.Response(text=INDEX_HTML_CONTENT, content_type='text/html')

@contextmanager
def send_file(file_path: str, file_name: str = None):
    if file_name is None:
        head, tail = os.path.split(file_path)
        file_name = tail

    async def redirect(request: aioweb.Request):
        return aioweb.HTTPFound(file_name)

    async def handle_get(request: aioweb.Request):
        print(f"Sending `{file_path}`.")
        return aioweb.FileResponse(path=file_path)

    app = aioweb.Application()
    app.router.add_get('/', redirect)
    app.router.add_get('/' + file_name, handle_get)
    
    with _run_http_server(app) as (loop, port):
        with _expose_ngrok(port) as public_url:
            yield loop, public_url

@contextmanager
def receive_file(dest_dir: str = None):
    async def handle_post(request: aioweb.Request):
        upload_file_name = request.match_info['upload_file_name']

        c_dest_dir = dest_dir

        if c_dest_dir is None:
            c_dest_dir = os.getcwd()

        dest_file_path = os.path.join(c_dest_dir, upload_file_name)

        print(f"Received `{upload_file_name}`.")
        print(f"Okay to save to `{dest_file_path}`?")
        yes = await _ask_user_yes_or_no()

        if yes:
            data = await request.read()

            with open(dest_file_path, 'wb') as f:
                f.write(data)
            
            return aioweb.Response()
        else:
            return aioweb.Response(text="File rejected.",status=400)

    app = aioweb.Application()
    app.router.add_get('/', _index)
    app.router.add_post('/{upload_file_name}', handle_post)
    
    with _run_http_server(app) as (loop, port):
        with _expose_ngrok(port) as public_url:
            yield loop, public_url



