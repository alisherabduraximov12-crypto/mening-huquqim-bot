==> Downloading cache...
==> Cloning from https://github.com/alisherabduraximov12-crypto/mening-huquqim-bot
==> Checking out commit 7fd4bbbce2cbbe219167e24e909c78f834476ca6 in branch main
==> Downloaded 2.2MB in 5s. Extraction took 0s.
==> Using Python version 3.14.3 (default)
==> Docs on specifying a Python version: https://render.com/docs/python-version
==> Installing Python version 3.14.3...
==> Using Poetry version 2.1.3 (default)
==> Docs on specifying a Poetry version: https://render.com/docs/poetry-version
==> Running build command 'pip install -r requirements.txt'...
Collecting Flask (from -r requirements.txt (line 1))
  Using cached flask-3.1.3-py3-none-any.whl.metadata (3.2 kB)
Collecting requests (from -r requirements.txt (line 2))
  Using cached requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
Collecting gunicorn (from -r requirements.txt (line 3))
  Using cached gunicorn-26.2.0-py3-none-any.whl.metadata (5.5 kB)
Collecting blinker>=1.9.0 (from Flask->-r requirements.txt (line 1))
  Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
Collecting click>=8.1.3 (from Flask->-r requirements.txt (line 1))
  Using cached click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
Collecting itsdangerous>=2.2.0 (from Flask->-r requirements.txt (line 1))
  Using cached itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
Collecting jinja2>=3.1.2 (from Flask->-r requirements.txt (line 1))
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting markupsafe>=2.1.1 (from Flask->-r requirements.txt (line 1))
  Downloading markupsafe-3.0.4-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Collecting werkzeug>=3.1.0 (from Flask->-r requirements.txt (line 1))
  Using cached werkzeug-3.1.9-py3-none-any.whl.metadata (4.1 kB)
Collecting charset_normalizer<4,>=2 (from requests->-r requirements.txt (line 2))
  Using cached charset_normalizer-3.5.2-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (46 kB)
Collecting idna<4,>=2.5 (from requests->-r requirements.txt (line 2))
  Using cached idna-3.20-py3-none-any.whl.metadata (7.2 kB)
Collecting urllib3<3,>=1.26 (from requests->-r requirements.txt (line 2))
  Using cached urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
Collecting certifi>=2023.5.7 (from requests->-r requirements.txt (line 2))
  Using cached certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
Using cached flask-3.1.3-py3-none-any.whl (103 kB)
Using cached requests-2.34.2-py3-none-any.whl (73 kB)
Using cached charset_normalizer-3.5.2-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (255 kB)
Using cached idna-3.20-py3-none-any.whl (69 kB)
Using cached urllib3-2.8.0-py3-none-any.whl (135 kB)
Using cached gunicorn-26.2.0-py3-none-any.whl (228 kB)
Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
Using cached certifi-2026.7.22-py3-none-any.whl (136 kB)
Using cached click-8.5.0-py3-none-any.whl (125 kB)
Using cached itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Downloading markupsafe-3.0.4-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (23 kB)
Using cached werkzeug-3.1.9-py3-none-any.whl (228 kB)
Installing collected packages: urllib3, markupsafe, itsdangerous, idna, gunicorn, click, charset_normalizer, certifi, blinker, werkzeug, requests, jinja2, Flask
Successfully installed Flask-3.1.3 blinker-1.9.0 certifi-2026.7.22 charset_normalizer-3.5.2 click-8.5.0 gunicorn-26.2.0 idna-3.20 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.4 requests-2.34.2 urllib3-2.8.0 werkzeug-3.1.9
[notice] A new release of pip is available: 25.3 -> 26.2.1
[notice] To update, run: pip install --upgrade pip
==> Uploading build...
==> Uploaded in 1.8s. Compression took 1.3s
==> Build successful 🎉
==> Deploying...
==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
==> Running 'gunicorn app:app'
[2026-10-04 06:58:30 +0000] [58] [INFO] Starting gunicorn 26.2.0
[2026-10-04 06:58:30 +0000] [58] [INFO] Listening at: http://0.0.0.0:10000 (58)
[2026-10-04 06:58:30 +0000] [58] [INFO] Using worker: sync
[2026-10-04 06:58:30 +0000] [59] [INFO] Booting worker with pid: 59
127.0.0.1 - - [04/Oct/2026:06:58:31 +0000] "HEAD / HTTP/1.1" 200 0 "-" "Go-http-client/1.1"
[2026-10-04 06:58:31 +0000] [58] [INFO] Control socket listening at /opt/render/.gunicorn/gunicorn.ctl
==> Your service is live 🎉
127.0.0.1 - - [04/Oct/2026:06:58:37 +0000] "GET / HTTP/1.1" 200 27 "-" "Go-http-client/2.0"
==> 
==> ///////////////////////////////////////////////////////////
==> 
==> Available at your primary URL https://mening-huquqim-bot.onrender.com
==> 
==> ///////////////////////////////////////////////////////////
