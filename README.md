# tibber2graphite
Fetch data from tibber API and feed it to graphite

# Howto

Install requrements

```
pip install -r requrements.txt
```

Change etc/client.ini to your environment. Change token, home, useragent, host and prefix. You will find your HOME-ID here: https://developer.tibber.com/explorer

Load your personal token and execute
```
{
  viewer {
    homes {
      id
    }
  }
}
```

To start fetching, execute ```fetch_rt.py```, preferable in a screen or as a service (see systemd/tibberrt.service as example)