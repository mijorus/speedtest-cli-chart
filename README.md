# Speeedtest Graph
![screenshot](https://raw.githubusercontent.com/mijorus/speedtest-cli-chart/master/screenshot.png)
This is a pretty simple python script that will output an html file with a graph showing your connection speed history.
It was develped to be used in a cronjob on a Raspberry Pi running Raspbian Buster, but it is very simple code which should run on other systems as well.

## Requires
This script requires Ookla's [official CLI tool](https://www.speedtest.net/apps/cli) to be installed on the system.
I found it more precise and reliable on a gigabit connection than the open source python version `speedtest-cli` you might be familiar with. 

The script also requires:
```python
pip install iso8601
```
## Usage
```sh
python3 speedtest-cron.py --script-path=<path to the speedtest-cli script>
```

By default the script will sleep for a random amount of secods (less than a minute don't worry) in order to avoid high traffic on Speedtest.net's servers and possibly a failure of the test.

You can override this behavior with
```sh
python3 speedtest-cron.py --no-sleep
``` 

You can show the results in the terminal with:
```sh
python3 speedtest-cron.py --show
```

