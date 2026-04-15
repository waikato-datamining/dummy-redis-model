# dummy-redis-model
Emulates a Deep Learning model that processes data via Redis and sends back predictions.

Only used for development.


## Installation

From Github repository:

```bash
pip install git+https://github.com/waikato-datamining/dummy-redis-model.git
```


## Command-line

```
usage: drm-emulate [-h] [--redis_host HOST] [--redis_port PORT]
                   [--redis_password PASSWORD] [--redis_password_env PASSWORD]
                   [--redis_db DB] --redis_in CHANNEL --redis_out CHANNEL
                   [--redis_timeout NUM] -o
                   {bluechannel-png,grayscale-png,indexed-png,opex} [-d SEC]
                   [--labels [LABEL ...]] [-n NUM] [-v]
                   [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Emulates a Deep Learning model processing data via Redis.

options:
  -h, --help            show this help message and exit
  --redis_host HOST     The redis server to connect to (default: localhost)
  --redis_port PORT     The port the redis server is listening on (default:
                        6379)
  --redis_password PASSWORD
                        The password to use for connecting (default: None)
  --redis_password_env PASSWORD
                        The environment variable to obtain the password from
                        to use for connecting (default: None)
  --redis_db DB         The redis database to use (default: 0)
  --redis_in CHANNEL    The redis channel to receive the data from (default:
                        None)
  --redis_out CHANNEL   The redis channel to publish the processed data on
                        (default: None)
  --redis_timeout NUM   The timeout to use for the pubsub thread sleep_time
                        parameter. (default: 0.01)
  -o {bluechannel-png,grayscale-png,indexed-png,opex}, --output {bluechannel-png,grayscale-png,indexed-png,opex}
                        The type of output to generated. (default: None)
  -d SEC, --delay SEC   The delay between receiving the data and generating
                        the output in seconds. (default: 0.5)
  --labels [LABEL ...]  The labels to generate. (default: None)
  -n NUM, --num_objects NUM
                        The number of random object detection objects to
                        generate. (default: 10)
  -v, --verbose         Whether to be more verbose with the output. (default:
                        False)
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
```

