.. highlight:: shell

============
Contributing
============


Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

To improve tracking of who did what, and to clarify the relationship
between the project and the contributor, we require a "sign-off" on patches
and pull requests submitted to this project. Instructions for how to do the
sign off are provided below.

Signing off certifies that you agree with the following:


Developer's Certificate of Origin 1.1
-------------------------------------


By making a contribution to this project, I certify that:

        (a) The contribution was created in whole or in part by me and I
            have the right to submit it under the open source license
            indicated in the file; or

        (b) The contribution is based upon previous work that, to the best
            of my knowledge, is covered under an appropriate open source
            license and I have the right under that license to submit that
            work with modifications, whether created in whole or in part
            by me, under the same open source license (unless I am
            permitted to submit under a different license), as indicated
            in the file; or

        (c) The contribution was provided directly to me by some other
            person who certified (a), (b) or (c) and I have not modified
            it.

        (d) I understand and agree that this project and the contribution
            are public and that a record of the contribution (including all
            personal information I submit with it, including my sign-off) is
            maintained indefinitely and may be redistributed consistent with
            this project or the open source license(s) involved.

To certify you agree with DCO, you will need to add the following line at
the end of each commit you submit to the project::

	Signed-off-by: Random J Developer <random@developer.example.org>

You must sign off with your real name as we unfortunately cannot accept
pseudonyms or anonymous contributions per this agreement.

You can do this easily in git by using ``-s`` when you run ``git commit``.
An example is provided in the "Get Started" section.


Ways to Contribute
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

The best way to send feedback is to file an issue at
https://github.com/BonnyCI/shuffleboard/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.


Get Started!
------------

Ready to contribute? First you need to set up your development environment:

You can either use a VM and install Python >= 3.5 or use pyenv if you're not
a fan of mucking around with system Python
(https://github.com/yyuu/pyenv-installer)

Here's how to set up `shuffleboard` for local development.

1. Clone the `shuffleboard` repo.

2. Create a virtualenv (venv-shuffleboard) and activate it

3. Install dependencies
   $ pip install -r requirements.txt

4. If you are using an IDE or editor that drops files in your working
directory, add them to the .gitignore

Next, find something to work on:

Larger work items are identified by Milestones. Each of these milestones is
associated with several Issues that represent smaller units of work.

Development is tracked in a Github Project:
https://github.com/BonnyCI/shuffleboard/projects/1

Once you've found something to work on, assign the issue to yourself and add
 the label "In Progress". Then, create a branch and push your changes there.

1. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

2. When you're done making changes, check that your changes pass flake8 and
the tests, including testing other Python versions with tox::

    $ flake8 shuffleboard tests
    $ python setup.py test or py.test
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes::

If you haven't read the above DCO agreement above, please do so. You need to
add a "signed-off" line to the end the commits you submit to the project to
certify that you agree with the terms of the DCO above::

    $ git add .
    $ git commit -s -m "Your detailed description of your changes."

7. Push your branch to GitHub::

    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.


Automate the Sign Off
---------------------

To make integrating the sign-off in your commits easier, you can define a
git alias or you can create a local git hook.

By automating the sign off, you won't have to remember to use the "-s" flag
each time and risk a rejected Pull Request.


Git Alias
~~~~~~~~~

The easiest way to set this up is to create a git alias. While you can't
replace the "commit" command, you can make a command you'll remember to use::

    $ git config alias.sign "commit -s"


Git Hook
~~~~~~~~

The other way to automate the sign off is to write a git hook to populate
your commit message with the sign off text. The prepare-commit-msg hook is
the most straightforward option for adding the sign off to your commit
messages. Git provides sample files for each of these hooks in the
.git/hooks folder. Instructions are at the top explaining each of the
samples and how to activate the hook.

1. Open the prepare-commit-msg.sample and uncomment the last example::

    $ nano .git/hooks/prepare-commit-msg.sample

2. Activate the prepare-commit-msg hook by dropping the suffix::

    $ cp .git/hooks/prepare-commit-msg.sample .git/hooks/prepare-commit-msg


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. Rebase commits to as few as possible and try to avoid a lot of confusing
one-off commits
2. Write a clear commit message that explains what the commit is about
3. Reference the issue# the commit is associated with. If you don't have an
issue to associate it with, create one and assign it to the milestone you
are currently working on.
4. At least one other person must approve the change before it can be merged to master.
