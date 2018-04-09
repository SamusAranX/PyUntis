# PyUntis
PyUntis is basically an API wrangler that makes the Untis API's output more readable.

I use it in conjunction with [`PyUntis-Site`](https://github.com/SamusAranX/PyUntis-Site) to create self-hosted displays of sorts for WebUntis timetables.

## Features
* Supports multiple schools at once, each with their own output folder
* If your school can be found via the Untis app's search feature, you can use its name and PyUntis will fill in its server info. This is useful if your school's Untis server changes frequently.
* Built for use with [`PyUntis-Site`](https://github.com/SamusAranX/PyUntis-Site), but if you're feeling adventurous, you can build your own site instead.

## Requirements

* Python 3.6
* [`requests`](http://docs.python-requests.org/en/master/)
* [`PyICU`](https://pypi.python.org/pypi/PyICU/) (optional, provides better, locale-independent sorting methods)

## Usage

Check out [`config_example.json`](config_example.json). Replace the example values in there with those of your school, set the `planDir` variable to the desired output folder, and rename the file to `config.json`.

Once everything's set, just do `python3.6 PyUntis.py` and watch a bunch of JSON files appear in the `planDir` directory.

If you're using some form of Linux and want things to be slightly easier, you can execute `generate_plan_example.sh` instead of `PyUntis.py`. The script will set the current directory for you, making sure that everything goes where it should go.

If you, like me, host [`PyUntis-Site`](https://github.com/SamusAranX/PyUntis-Site) as a timetable display and want all data to be refreshed automatically, make sure to put it into your crontab like this:

`*/5 * * * * /home/untis/PyUntis/generate_plan.sh > /var/www/example.org/plan/plan.log 2>&1`

The script takes about 38 seconds to fetch all data for two schools, so running it every five minutes should be sufficient.

## Feedback and support
Just tweet at me [@SamusAranX](https://twitter.com/SamusAranX) or [drop me a mail](mailto:hallo@peterwunder.de).
Feel free to create an issue if you encounter any crashes, bugs, etc.: [PyUntis Issues](https://github.com/SamusAranX/PyUntis/issues)