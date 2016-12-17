shuffleboard
------------

Developer activity integration for project reporting and tracking

PROJECT STATUS
~~~~~~~~~~~~~~


DONE:
+++++


IN PROGRESS:
++++++++++++

1. Get GH Issues and Issue events

TODO:
++++

2. Get pull request and merge events from Github
3. Run Manually
4. Store Collected Data / Define Reports
5. Get Upstream Activity from Gerrit and Storyboard
6. Run as a Process
7. Figure out what's next!


DEVELOPMENT PHASES
~~~~~~~~~~~~~~~~~~

Phase I: Functionality (make it work, don't care about code quality)
- run manually, only get data since last run
- eventually this should just run all the time with a monitoring process

Phase II: Refactor (improve design and code quality)
- add test coverage to make sure stuff doesn't break in the refactor
- move things out into libraries, use classes, modularize things
- remove hard-coded things to settings files and/or command line args
