cd "`dirname "$0"`"
source ./venv/bin/activate
python python/xlsx/toStrings.py
python python/parser/segue.py
python python/parser/plist.py
python python/image/resize.py