# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.4.0]
### Breaking changes
 - This version is compatible with version of the sc-machine 0.10.0. All API methods were redesigned. Incorrect ones were removed, new ones were added. See table below, to learn more about changes.
   
  | Deprecated method                       | Substitution method                        | 
  |-----------------------------------------|--------------------------------------------|
  | create_action_result                    | generate_action_result                     |
  | create_action                           | generate_action                            |
  | create_nodes                            | generate_nodes                             |
  | create_node                             | generate_node                              |
  | create_links                            | generate_links                             |
  | create_link                             | generate_link                              |
  | create_edges                            | generate_connectors                        |
  | create_edge                             | generate_connector                         |
  | create_binary_relation                  | generate_binary_relation                   | 
  | create_role_relation                    | generate_role_relation                     |
  | create_norole_relation                  | generate_non_role_relation                 |
  | check_edge                              | check_connector                            |
  | get_edge                                | search_connector                           |
  | get_edges                               | search_connectors                          |
  | get_system_idtf                         | get_element_system_identifier              |
  | search_norole_relation_template         | search_non_role_relation_template          |
  | get_element_by_role_relation            | search_element_by_role_relation            |
  | get_element_by_norole_relation          | search_element_by_non_role_relation        |
  | delete_edges                            | erase_connectors                           |
  | delete                                  | erase                                      |

### Added
- ScKeynodes method `erase`
- Common utils methods: `generate_nodes`, `generate_node`, `generate_links`, `generate_link`, `generate_connectors`, `generate_connector`, `generate_binary_relation`, `generate_role_relation`, `generate_non_role_relation`, `check_connector`, `search_connector`, `search_connectors`, `get_element_system_identifier`, `search_non_role_relation_template`, `search_element_by_role_relation`, `search_element_by_non_role_relation`, `erase_connectors`
- Action utils methods: `generate_action_result`, `generate_action`

### Deprecated
- ScKeynodes method `delete`
- Common utils methods: `create_nodes`, `create_node`, `create_links`, `create_link`, `create_edges`, `create_edge`, `create_binary_relation`, `create_role_relation`, `create_norole_relation`, `check_edge`, `get_edge`, `get_edges`, `get_system_idtf`, `search_norole_relation_template`, `get_element_by_role_relation`, `get_element_by_norole_relation`, `delete_edges`
- Action utils methods: `create_action_result`, `create_action`

### Changed
- All answers are replaced with results

## [v0.3.0]
### Changed
- All questions are replaced with actions

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
