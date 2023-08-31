# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.2.0]
### Changed
- Removed reconnection for py-sc-client 0.3.0

## [v0.1.2]
### Fixed
- Wait agent bug: it failed if action finished before

## [v0.1.1] - [YANKED]
### Added
- Atomic operations with actions: create, add arguments and call
### Changed
- Wait agent function uses ScEvent

## [v0.1.0]
### Added
- README and LICENSE files
- ScKeynodes class for caching identifiers and ScAddr objects. Easy access to rrel keynodes
- ScAgent class for handling a single ScEvent
- ScModule class for handling a multiple ScAgent
- ScServer class for modules serving
- ScSet, ScStructure, ScOrientedSet and ScNumberedSet classes for creating complex structures and manipulations
- List of common utils for basic manipulations with knowledge base
- List of action utils for agent development based on actions
- List of iterate utils for easy passing the same type of data
- Code linting tools: isort, pylint, black, pre-commit
- Documentation for contributors and developers
- CI for checking messages of commits
- CI for code linting
- CI for the testing package on multiple environments and python versions
- CI for publishing package on PyPi
