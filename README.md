# Setup

For frontend, see README in that directory.

For music_server, set up a pipenv environment with something similar to the following:

```
cd music_server
pipenv shell
pipenv install
python manage.py migrate
python manage.py createsuperuser --email admin@example.com --username admin
```

This should set up the Django server for the most part. However, additional setup is required for some of the python libraries in use.

- Set up music21 via `python -m music21.configure`. See [https://web.mit.edu/music21/doc/usersGuide/usersGuide_01_installing.html](https://web.mit.edu/music21/doc/usersGuide/usersGuide_01_installing.html) for more details on setting up music21 for different systems (OSX seems to require special care).
