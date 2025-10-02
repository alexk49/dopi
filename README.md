# dopi

Python application for bulk checking DOIs resolve to the expected host. Can be accessed at [https://dopi.booksanon.com](https://dopi.booksanon.com), run locally, or just run as a cli.

Dopi can be used to bulk check whether DOIs resolve to a specified host.  

It can be used via:
- A web app: [https://dopi.booksanon.com](https://dopi.booksanon.com)
- A local instance of the web app
- A command-line interface (CLI)

## Install and setup

The src/cli.py file can be run without any additional packages but the web application requires bottle and gunicorn to be installed.

```
git clone https://github.com/alexk49/dopi.git
cd dopi
python -m venv .venv
source .venv/bin/activate
pip install -e .           # install core package for web app
pip install -e .[test,lint]  # install dev dependencies
npm install                # install JS tooling: jest, eslint and prettier if required
```

This will also create an executable called dopi that can be used to run the cli commands.

### env file

Sourcing of the .env files is handled in deploy.sh but when running locally you will need to source them in your shell. One way of doing this is:

```
export $(grep -v '^#' .env | xargs)
```

As CrossRef ask for an email address to be added to the header requests when making calls to their API, you must set an environment variable for an email, either in an .env file in the shell:

```
EMAIL_ADDRESS=me@email.com
```

More variables are need to be set for full deployment.

## deployment

The web application requires .env variables to be set for the following:

```
# email credentials
# you will probably need to set up an app specific password for email
EMAIL_ADDRESS=me@email.com
EMAIL_PASSWORD=email-password

# bottle variables, these are set to defaults in config.py
HOST=
PORT=
DEBUG=

# docker variable
HOST_PORT=
```

The bottle application can be deployed into a docker container with:

```
./deploy.sh
```

A git hook has been set up run this script upon post receive. To deploy, run:

```
git push prod main
```

The app can be run locally - outside of a docker container with:

```
dopi -run
```

## web app

The web app uses bottle and is just a wrapper for submitting DOIs to be checked.

The actual calls to the CrossRef API are done as a background task.

Note: the background task may behave inconsistently in Bottle's debug mode. For local testing of background tasks, you may need to set `DEBUG=FALSE` in your .env file.

## cli

Some basic wrapper commands have been provided for CI:

```
# run app locally
dopi --run

# run linters and tests:
dopi --lint 
dopi --test 
```

### usage

Check a single DOI resolves to nature.com:

```
dopi --doi 10.1038/nphys1170 --resolving-host nature.com
```

Check multiple DOIs resolve to nature.com:

```
dopi --dois 10.1038/nphys1170,10.1126/science.169.3946.635 -rh nature.com
```

Check a .csv file of DOIs resolves to somewhere.com and get results written to a .csv:

```
dopi --file path/to/dois.csv --resolving-host somewhere.com --write-to-csv
```

The .csv file of DOIs should have DOIs in the first column and nothing else.

The output .csv file will be found in a directory called /complete.

Pass a complete .csv file with email, resolving host and DOIs, and write results to .csv:

```
dopi --complete-csv path/to/full_input.csv --write-to-csv
```

The `--complete-csv` file should contain a single column in this order:

```
hello@email.com
hostsite-dois-should-resolve-to
doi1
doi2
```

Send emails from the cli - requires email address and password set as environment variables, mainly used for testing setup.

```
dopi emailer --recipient user@example.com --subject "Results" --body "See attached." --attachment results.csv
```

For full list of options run:

```
dopi --help
```

## Contributing

Pull requests, contributions and suggestions for improvement are welcome!

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
