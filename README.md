# cryomonit
the app is meant for the monitoring of a sensor. It contains several containers: \
    - influxdb \
    - grafana \
    - a home made rundb which checks a given data folder and fills the influxdb \
The format of data is the following:\ 
    - one file per day with the name YYYYMMDD \
    - in the file one data per line with the format:\
        HH:MM:SS value\
        HH:MM:SS value\
        ...\


Here are a set of commands to run the app: \
1. in the docker-compose.yml file: \
    change the data source path  \ 
2. type  \
docker-compose run -d sensor python3 -u rundb.py influxdb 8086 datafolder tagname measuredvaluename -r tagnametoreset -t Europe/Paris \
where: \
    influxdb: is fixed \ 
    8086: is fixed \
    datafolder: is at minimum /data/ but can be /data/anotherfolder if the data you are looking for are in sourcefolder/anotherfolder \
    tagname: is the name of the setup (for instance cryo1, or cryo2 etc) \
    measuredvaluename: is how you want to name the physical parameter measured, for instance P or T  \
    tagnametoreset: this option allows you to reset the data with the given tag name and rewrite all the files present in the data folder \
                    the option all removes all the tags \
    timezone: Paris time by default so you really want to change that if you don't have the chance to work there !\ 
              The string you need to provide is the pytz list for instance: America/Chicago or UTC  \ 
               to print all of them type in a python terminal:  \
                import pytz \ 
                for tz in pytz.all_timezones: \
                    print tz \
