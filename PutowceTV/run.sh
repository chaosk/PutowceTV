#!/bin/bash
. venv/bin/activate
crossbar start &>crossbar.log
echo "crossbar started"
sleep 2
python app.py &>tv.log
echo "app started"
midori -e Fullscreen -a http://localhost:8000/client