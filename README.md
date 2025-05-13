<h1>Run the script:</h1>

`python -m locust -f script.py --host=http://172.30.30.78:8000 --headless --users 200 --spawn-rate 5 --run-time 3m --csv=login_results`

<p><h2>Considering:</h2> <br/>
script.py -> name of your python script <br/>
172.30.30.78:8000 -> the sso is running in this ip<br/>
–users 200 -> Concurrent hits per second<br/>
–spawn-rate 5 -> Increase the user by 5 per second until it reaches to 200<br/>
3m -> the load will run for 3 minutes<br/>
login_results -> the result will be exported to login_results.csv file<br/>
</p>
<h2>Prerequisite:</h2>
Python 3.12.8 (this version is important) <br/>
pip <br/>
Locust (python framework): pip install locust <br/>
BeatifulSoup (python library): pip install beautifulsoup4 <br/>


