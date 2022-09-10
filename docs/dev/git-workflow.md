### Workflow
When contributing code, you'll want to follow this checklist:

1. Fork the repository on GitHub.
2. Run the tests to confirm they all pass on your system. If they don't, you'll
   need to investigate why they fail. If you're unable to diagnose this
   yourself, raise it as a bug report by following the guidelines in this
   document: [bug-reports](https://github.com/ostis-ai/py-sc-kpm/blob/d59362a50c6c9b8bbbc6d655da6854e59abb451a/.github/ISSUE_TEMPLATE/bug_report.md).
3. Write tests that demonstrate your bug or feature. Ensure that they fail.
4. Make your change.
5. Run the entire test suite again, confirming that all tests pass *including
   the ones you just added*.
6. Send a GitHub Pull Request to the main repository's ``main`` branch.
   GitHub Pull Requests are the expected method of code collaboration on this
   project.


This project uses [Git-Flow](https://www.gitkraken.com/learn/git/git-flow),
[git-flow tool](https://github.com/nvie/gitflow) can be used.

The Git flow branches that we are interested in are the following branches :

* `feature/*`(short lived) - new functional, docs, build, CI, test development work
* `fix/*`(short lived) - fixes of functional, docs, build, CI, test development work
* `release/*` (short lived) - release candidate, bug fixes for a release, deploys to a production environment
* `main` (long lived) - latest development work, deploys to a dev environment
* `hotfix/*` (short lived) - urgent fixes to production
