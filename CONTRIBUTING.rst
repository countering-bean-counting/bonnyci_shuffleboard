.. highlight:: shell

============
Contributing
============


Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/missaugustina/shuffleboard/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Shuffleboard could always use more documentation, whether as part of the
official Shuffleboard docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/missaugustina/shuffleboard/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? First you need to set up your development environment:

You can either use a VM and install Python >= 3.5 or use pyenv if you're not a fan of mucking around with system Python
(https://github.com/yyuu/pyenv-installer)

Here's how to set up `shuffleboard` for local development.

- git clone from the project url
- cd shuffleboard
- create a virtualenv (venv-shuffleboard) and activate it
- pip install -r requirements.txt

1. Clone the `shuffleboard` repo.

2. Create a virtualenv (venv-shuffleboard) and activate it

3. Install dependencies
   $ pip install -r requirements.txt

4. If you are using an IDE or editor that drops files in your working directory, add them to the .gitignore

Next, find something to work on:

Larger work items are identified by Milestones. Each of these milestones is associated with several Issues that
represent smaller units of work.

The current milestone under development is tracked in the README for now. This will change either to a Trello board or
Github project board in the future.

Once you've found something to work on: create a branch and push your changes there.

1. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

2. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ flake8 shuffleboard tests
    $ python setup.py test or py.test
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature


7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. Rebase commits to as few as possible and try to avoid a lot of confusing one-off commits
2. Write a clear commit message that explains what the commit is about
3. Reference the issue# the commit is associated with. If you don't have an issue to associate it with, create one and
assign it to the milestone you are currently working on.
4. At least one other person must approve the change before it can be merged to master.
