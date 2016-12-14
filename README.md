# shuffleboard
Integrate GHE, Github, and Trello for project reporting and tracking

PROJECT STATUS

DONE:

IN PROGRESS:

1) Get Issues and Issue events
- from github

TODO:

2) Create a card for new Issues
- in Trello

3) Update issue card for Issue Events
- in Trello

4) Get Pull Request Events (incl merges)
- from ghe
- from github (eventually)

5) Link PR events to Issues
- question: how to reference issues? where should they be stored? application cache, re-pull + re-process from github? both?

6) Update issue card for PR Events
- in Trello

Phase I: Functionality (make it work, don't care about code quality)
- run manually, gets events based on history and compares with with what's already been done (see query options for github, should have option to specify time frame for events)
- eventually this should just run all the time with a monitoring process

Phase II: Refactor (improve design and code quality)
- add test coverage to make sure stuff doesn't break in the refactor
- move things out into libraries, use classes, modularize things
- remove hard-coded things to settings files and/or command line args

DEVELOPMENT HOW TO

First you need to set up your development environment:

1) Set up Python:
- use a VM and the target OS's system Python
- use pyenv - https://github.com/yyuu/pyenv-installer

2) Get the project
- git clone from the project url
- cd shuffleboard
- create a virtualenv (venv-shuffleboard) and activate it
- pip install -r requirements.txt

3) If you are using an IDE or editor that drops files in your working directory, add them to the .gitignore

Next, find something to work on:

Larger work items are identified by Milestones. Each of these milestones is associated with several Issues that represent smaller units of work.

The current milestone under development is tracked in this README for now. This will change either to a Trello board or Github project board in the future.

Once you've found something to work on, create a branch and push your changes there.
- rebase commits to as few as possible, try to avoid a lot of confusing one-off commits
- write a clear commit message that explains what the commit is about
- reference the issue# the commit is associated with. If you don't have an issue to associate it with, create one and assign it to the milestone you are currently working on.
- when ready, create a pull request for your branch
- At least one other person must approve the change before it can be merged to master
