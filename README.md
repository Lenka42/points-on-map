# points-on-map
Tornado server managing geo points

## Installation
* Create `python3` virtual environment and install requirements
```bash
virtualenv -p python3 env
. env/bin/activate
pip install -r requirements.txt
```
* Start tornado server
```bash
python app.py
```
By default server runs on `8888` port, so when you open http://localhost:8888 in your browser, 
you will see a page with map. You can add flag `--port=8000` to the command above to run server on your favourite port 
(you might also want to update `BASE_URL` constant in points.js file). You can use flag `--prettify` to make json data file human-friendly.