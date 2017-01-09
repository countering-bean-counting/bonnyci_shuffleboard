#!/usr/bin/env perl

# Events (they only provide the last 300)
# GET /users/:user/events
use strict;
use warnings;

`curl -i "https://api.github.com/users/BonnyCI/events?per_page=100" >> events1.json`;
`curl -i "https://api.github.com/users/BonnyCI/events?per_page=100&page=2" >> events2.json`;
`curl -i "https://api.github.com/users/BonnyCI/events?per_page=100&page=3" >> events3.json`;

# Make Folders
`mkdir projman`;
`mkdir hoist`;
`mkdir shuffleboard`;
`mkdir ci-plunder`;
`mkdir zuul`;

# Labels
# GET /repos/:owner/:repo/labels

`curl -i "https://api.github.com/repos/BonnyCI/projman/labels?per_page=100" >> projman/labels.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/labels?per_page=100" >> hoist/labels.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/labels?per_page=100" >> shuffleboard/labels.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/labels?per_page=100" >> ci-plunder/labels.json`;
`curl -i "https://api.github.com/repos/BonnyCI/zuul/labels?per_page=100" >> zuul/labels.json`;

# Milestones
# GET /repos/:owner/:repo/milestones

`curl -i "https://api.github.com/repos/BonnyCI/projman/milestones?per_page=100" >> projman/milestones.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/milestones?per_page=100" >> hoist/milestones.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/milestones?per_page=100" >> shuffleboard/milestones.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/milestones?per_page=100" >> ci-plunder/milestones.json`;
`curl -i "https://api.github.com/repos/BonnyCI/zuul/milestones?per_page=100" >> zuul/milestones.json`;

# Commits
# GET /repos/:owner/:repo/git/commits

`curl -i "https://api.github.com/repos/BonnyCI/projman/commits?per_page=100" >> projman/commits.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/commits?per_page=100" >> hoist/commits1.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/commits?per_page=100&page=2" >> hoist/commits2.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/commits?per_page=100&page=3" >> hoist/commits3.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/commits?per_page=100&page=4" >> hoist/commits4.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/commits?per_page=100&page=5" >> hoist/commits5.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/commits?per_page=100&page=6" >> hoist/commits6.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/commits?per_page=100" >> shuffleboard/commits.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/commits?per_page=100" >> ci-plunder/commits.json`;
`curl -i "https://api.github.com/repos/BonnyCI/zuul/commits?per_page=100" >> zuul/commits.json`;

# Issues
# GET /repos/:owner/:repo/issues

`curl -i "https://api.github.com/repos/BonnyCI/projman/issues?per_page=100&state=all" >> projman/issues.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/issues?per_page=100&state=all" >> shuffleboard/issues.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/issues?per_page=100&state=all" >> ci-plunder/issues.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/issues?per_page=100&state=all" >> hoist/issues.json`;
`curl -i "https://api.github.com/repos/BonnyCI/zuul/issues?per_page=100&state=all" >> zuul/issues.json`;

# Issue Comments
# GET /repos/:owner/:repo/issues/comments

`curl -i "https://api.github.com/repos/BonnyCI/projman/issues/comments?per_page=100" >> projman/issue_comments.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/issues/comments?per_page=100" >> shuffleboard/issue_comments.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/issues/comments?per_page=100" >> ci-plunder/issue_comments.json`;

# Pull Requests
# GET /repos/:owner/:repo/pulls

`curl -i "https://api.github.com/repos/BonnyCI/projman/pulls?per_page=100&state=all" >> projman/pull_requests.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/pulls?per_page=100&state=all" >> hoist/pull_requests.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/pulls?per_page=100&state=all" >> shuffleboard/pull_requests.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/pulls?per_page=100&state=all" >> ci-plunder/pull_requests.json`;
`curl -i "https://api.github.com/repos/BonnyCI/zuul/pulls?per_page=100&state=all" >> zuul/pull_requests.json`;

# Pull Request Comments
# GET /repos/:owner/:repo/pulls/comments

`curl -i "https://api.github.com/repos/BonnyCI/projman/pulls/comments?per_page=100" >> projman/pull_request_comments.json`;
`curl -i "https://api.github.com/repos/BonnyCI/hoist/pulls/comments?per_page=100" >> hoist/pull_request_comments.json`;
`curl -i "https://api.github.com/repos/BonnyCI/shuffleboard/pulls/comments?per_page=100" >> shuffleboard/pull_request_comments.json`;
`curl -i "https://api.github.com/repos/BonnyCI/ci-plunder/pulls/comments?per_page=100" >> ci-plunder/pull_request_comments.json`;
`curl -i "https://api.github.com/repos/BonnyCI/zuul/pulls/comments?per_page=100" >> zuul/pull_request_comments.json`;

`find . -name "*.json" | xargs sed -i '1,24 d'`;
`find . -name "events*.json" | xargs sed -i '1,2 d'`;
