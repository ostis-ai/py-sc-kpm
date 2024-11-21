# py-sc-kpm

The python implementation of the knowledge processing machine (kpm)
for [sc-machine](https://github.com/ostis-ai/sc-machine).
Library provides tools for interacting with knowledge bases.
Communication with server is implemented in separate library
named [py-sc-client](https://github.com/ostis-ai/py-sc-client).
This module is compatible with 0.10.0 version
of [OSTIS Platform](https://github.com/ostis-ai/ostis-web-platform).

# API Reference

1. [Classes](#classes)
   + [ScKeynodes](#sckeynodes)
   + [ScAgent](#scagent-and-scagentclassic)
   + [ScModule](#scmodule)
   + [ScServer](#scserver)
2. [Utils](#utils)
   + [Common utils](#common-utils)
   + [Generating utils](#generating-utils)
   + [Retrieve utils](#retrieve-utils)
   + [Action utils](#action-utils)
3. [Use-cases](#use-cases)

## Classes

The library contains the python implementation of useful classes and functions to work with the sc-memory.

### ScKeynodes

Class which provides the ability to cache the identifier and ScAddr of keynodes stored in the KB.

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes

# Get the provided identifier
ScKeynodes["identifier_of_keynode"]  # Returns an ScAddr of the given identifier

# Get the unprovided identifier
ScKeynodes["not_stored_in_kb"]  # Raises InvalidValueError if an identifier doesn't exist in the KB
ScKeynodes.get("not_stored_in_kb")  # Returns an invalid ScAddr(0) in the same situation

# Resolve identifier
ScKeynodes.resolve("my_class_node", sc_type.CONST_NODE_CLASS)  # Returns the element if it exists, otherwise generates
ScKeynodes.resolve("some_node", None)  # Returns the element if it exists, otherwise returns an invalid ScAddr(0)

# Erase identifier
ScKeynodes.erase("identifier_to_erase")  # Erase keynode from kb and ScKeynodes cache

# Get rrel node
ScKeynodes.rrel_index(1)  # Returns valid ScAddr of 'rrel_1'
ScKeynodes.rrel_index(11)  # Raises KeyError if index more than 10
ScKeynodes.rrel_index("some_str")  # Raises TypeError if index is not int
```

### ScAgent and ScAgentClassic

A classes for handling a single ScEvent. Define your agents like this:

```python
from sc_client.models import ScAddr
from sc_kpm import ScAgent, ScAgentClassic, ScResult


class ScAgentTest(ScAgent):
    def on_event(self, class_node: ScAddr, connector: ScAddr, action_node: ScAddr) -> ScResult:
        ...
        return ScResult.OK


class ScAgentClassicTest(ScAgentClassic):
    def on_event(self, class_node: ScAddr, connector: ScAddr, action_node: ScAddr) -> ScResult:
        # ScAgentClassic automatically checks its action
        ...
        return ScResult.OK
```

For the ScAgent initialization you should define the sc-element and the type of the ScEvent.

For the ScAgentClassic initialization you should define the identifier of the action class node and arguments of the ScAgent. `subscription_element` is set to the `action_initiated` keynode by default. `event_class` is set to the `ScEventType.AFTER_GENERATE_OUTGOING_ARC` type by default.

**ScAgentClassic checks its action element automatically and doesn't run `on_event` method if checking fails.**

```python
from sc_client.constants import sc_type
from sc_client.constants.common import ScEventType
from sc_kpm import ScKeynodes

action_class = ScKeynodes.resolve("test_class", sc_type.CONST_NODE_CLASS)
agent = ScAgentTest(action_class, ScEventType.AFTER_GENERATE_OUTGOING_ARC)

classic_agent = ScAgentClassicTest("classic_test_class")
classic_agent_incoming = ScAgentClassicTest("classic_test_class", ScEventType.AFTER_GENERATE_INCOMING_ARC)
```

### ScModule

A class for handling multiple ScAgent objects.
Define your modules like this:

```python
from sc_kpm import ScModule

module = ScModule(
    agent1,
    agent2,
)
...
module.add_agent(agent3)
...
module.remove_agent(agent3)
```

_Note: you don't need remove agents in the end of program._

### ScServer

A class for serving, register ScModule objects.

Firstly you need connect to server. You can use connect/disconnect methods:

```python
from sc_kpm import ScServer

SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)
server.connect()
...
server.disconnect()
```

Or with-statement. We recommend it because it easier to use, and it's safe:

```python
from sc_kpm import ScServer

SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)
with server.connect():
    ...
```

After connection, you can add and remove your modules. Manage your modules like this:

```python
...
with server.connect():
    module = ScModule(...)
    server.add_modules(module)
    ...
    server.remove_modules(module)
```

But the modules are still not registered. For this use register_modules/unregister_modules methods:

```python
...
with server.connect():
    ...
    server.register_modules()
    ...
    server.unregister_modules()
```

Or one mode with-statement.
We also recommend to use so because it guarantees a safe agents unregistration if errors occur:

```python
...
with server.connect():
    ...
    with server.register_modules():
        ...
```

If you needn't separate connecting and registration, you can do it all using one command:

```python
with server.start():
    ...
# or
server.start()
...
server.stop()
```

There is also method for stopping program until a SIGINT signal (or ^C, or terminate in IDE) is received.
So you can leave agents registered for a long time:

```python
...
with server.connect():
    # Creating some agents
    with server.register_modules():
        # Registration some agents
        server.serve()  # Agents will be active until ^C
```

### ScSets

Sc-set is a construction that presents main node called `set_node` and linked elements.
There is no limit in types for sc-set elements:

![sc-set example](docs/schemes/png/set.png)

#### ScSet

- *sc_kpm.sc_sets*.**ScSet**

Class for handling simple sc-sets.
It is the parent class for `ScOrientedSet` and `ScNumberedSet`

Methods and properties:

1. *ScSet*(*elements: ScAddr, set_node: ScAddr = None, set_node_type: ScType = None) -> None

   Constructor of sc-set receives all elements to add, optional `set_node` and optional `set_node_type`.
   If you don't specify `set_node`, it will be generated with `set_node_type` (default CONST_NODE).

2. *ScSet*.**add**(*elements: ScAddr) -> None

   Add elements to the end of sc-set construction.

3. *ScSet*.**set_node** -> ScAddr

   Property to give the **main node** of sc-set.

4. *ScSet* == *ScSet* -> bool

   Check sc-sets have the same set_nodes.

5. *ScSet*.**elements_set** -> Set[ScAddr]

   Property to give all elements from sc-set as a set.
   Use it if you don't need order in ordered sets.

6. **iter**(*ScSet*) -> Iterator[ScAddr]

   Dunder method for iterating by sc-set.
   Lazy algorithm (ScOrientedSet and ScNumberedSet).

7. **len**(*ScSet*) -> int

   Fast dunder method to give **count of elements** (power of sc-set).

8. **bool**(*ScSet*) -> bool

   Dunder method for if-statement: True if there are elements in sc-set.

9. *ScSet*.**is_empty**() -> bool

   True if there are **no elements** in sc-set.

10. *ScAddr* **in** *ScSet* -> bool

    Dunder method: True if sc-set contains element.

11. *ScSet*.**clear**() -> bool

    Remove all elements from sc-set.

12. *ScSet*.**remove**(*elements: ScAddr) -> None

    Remove elements from sc-set.
    *WARNING*: method isn't optimized in ScOrientedSet and ScNumberedSet

```python
from sc_client.constants import sc_type
from sc_client.models import ScAddr

from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import generate_node, generate_nodes

# Example elements to add
example_set_node: ScAddr = generate_node(sc_type.CONST_NODE)
elements: list[ScAddr] = generate_nodes(*[sc_type.CONST_NODE] * 5)

# Init sc-set and add elements
empty_set = ScSet()

set_with_elements = ScSet(elements[0], elements[1])
set_with_elements.add(elements[2], elements[3])
set_with_elements.add(elements[4])

set_with_elements_and_set_node = ScSet(elements[2], set_node=example_set_node)
empty_set_with_specific_set_node_type = ScSet(set_node_type=sc_type.NODE_VAR)

# Get set node
set_node = empty_set.set_node
assert set_with_elements_and_set_node.set_node == example_set_node

# Get elements: list and set
assert set_with_elements.elements_set == set(elements)  # set view faster and safe

# Iterate by elements
for element in set_with_elements:
    print(element)

# Length, bool, is_empty, in
assert len(set_with_elements) == len(elements)
assert bool(set_with_elements)
assert not set_with_elements.is_empty()
assert empty_set.is_empty()
assert elements[2] in set_with_elements

# Clear and remove
set_with_elements.remove(elements[4])
assert len(set_with_elements), len(elements) - 1
set_with_elements.clear()
assert set_with_elements.is_empty()
```

##### ScStructure

If `set_node` has type `sc_type.CONST_NODE_STRUCTURE` construction is called sc-structure
and looks like a loop in SCg:

![structure](docs/schemes/png/structure.png)
![structure2](docs/schemes/png/structure_circuit.png)

- *sc_kpm*.**ScStructure**

Class for handling structure construction in the kb.
The same logic as in `ScSet`, but *set_node_type* if set CONST_NODE_STRUCTURE.
There are checks that set node has struct sc-type:

```python
from sc_kpm.sc_sets import ScStructure

sc_struct = ScStructure(..., set_node=..., set_node_type=...)

sc_struct = ScStructure(..., set_node=generate_node(sc_type.CONST_NODE))  # InvalidTypeError - not struct type
sc_struct = ScStructure(..., set_node_type=sc_type.CONST_NODE)  # InvalidTypeError - not struct type
```

#### Ordered sc-sets

ScOrientedSet and ScNumberedSet are ordered sc-constructions.
Child classes of ScSet, have the order in iteration and get list elements:

- *Sc{ordered}Set*.**elements_set** -> List[ScAddr]

  Get the list of all elements with order

##### ScOrientedSet

- *sc_kpm*.**ScOrientedSet**

![oriented_set_example](docs/schemes/png/oriented_set.png)

Class for handling sc-oriented-set construction.
Has marked arcs between arcs from set_node to elements.
Easy lazy iterating.
No access by index.

```python
from sc_client.constants import sc_type

from sc_kpm.sc_sets import ScOrientedSet
from sc_kpm.utils import generate_nodes


elements = generate_nodes(*[sc_type.CONST_NODE] * 5)
numbered_set = ScOrientedSet(*elements)
assert numbered_set.elements_list == elements
```

##### ScNumberedSet

- *sc_kpm*.**ScNumberedSet**

![numbered_set_example](docs/schemes/png/numbered_set.png)

Class for handling sc-numbered-set construction.
Set-node is set with numerating each element with rrel node.
Easy access to elements by index (index i is marked with rrel(i + 1))

```python
from sc_client.constants import sc_type

from sc_kpm.sc_sets import ScNumberedSet
from sc_kpm.utils import generate_nodes


elements = generate_nodes(*[sc_type.CONST_NODE] * 5)
numbered_set = ScNumberedSet(*elements)
assert numbered_set.elements_list == elements
assert numbered_set[2] == elements[2]
numbered_set[5]  # raise KeyError
```

## Utils

There are some functions for working with nodes, connectors, links: generate them, search, get content, erase, etc.
There is also possibility to wrap in set or oriented set.

## Common utils

There are utils to work with basic elements

_You can import these utils from `sc_kpm.utils`_

### Nodes generating

If you want to generate one or more nodes use these functions with type setting argument:

```python
def generate_node(node_type: ScType, sys_idtf: str = None) -> ScAddr: ...


def generate_nodes(*node_types: ScType) -> List[ScAddr]: ...
```

`sys_idtf` is optional name of keynode if you want to add it there.

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.utils.common_utils import generate_node, generate_nodes

lang = generate_node(sc_type.CONST_NODE_CLASS)  # ScAddr(...)
lang_en = generate_node(sc_type.CONST_NODE_CLASS)  # ScAddr(...)
assert lang.is_valid() and lang_en.is_valid()
elements = generate_nodes(sc_type.CONST_NODE, sc_type.NODE_VAR)  # [ScAddr(...), ScAddr(...)]
assert len(elements) == 2
assert all(element.is_valid() for element in elements)
```

### Connectors generating

For generating connector between **src** and **trg** with setting its type use **generate_connector** function:

```python
def generate_connector(connector_type: ScType, src: ScAddr, trg: ScAddr) -> ScAddr: ...

def generate_connectors(connector_type: ScType, src: ScAddr, *targets: ScAddr) -> List[ScAddr]: ...
```

```python
from sc_client.constants import sc_type
from sc_kpm.utils import generate_nodes
from sc_kpm.utils import generate_connector, generate_connectors

src, trg, trg2, trg3 = generate_nodes(*[sc_type.CONST_NODE] * 4)
connector = generate_connector(sc_type.CONST_PERM_POS_ARC, src, trg)  # ScAddr(...)
connectors = generate_connectors(sc_type.CONST_PERM_POS_ARC, src, trg2, trg3)  # [ScAddr(...), ScAddr(...)]
assert connector.is_valid()
assert all(connectors)
```

Function **is_valid()** is used for validation addresses of nodes or connectors.

### Links generating

For generating links with string type content (by default) use these functions:

```python
def generate_link(
        content: Union[str, int],
        content_type: ScLinkContentType = ScLinkContentType.STRING,
        link_type: ScType = sc_type.CONST_NODE_LINK
) -> ScAddr: ...


def generate_links(
        *contents: Union[str, int],
        content_type: ScLinkContentType = ScLinkContentType.STRING,
        link_type: ScType = sc_type.CONST_NODE_LINK,
) -> List[ScAddr]: ...
```

You may use **ScLinkContentType.STRING** and **ScLinkContentType.INT** types for content of generated links.

```python
from sc_client.constants import sc_type
from sc_client.models import ScLinkContentType
from sc_kpm.utils import generate_link, generate_links

msg = generate_link("hello")  # ScAddr(...)
four = generate_link(4, ScLinkContentType.INT)  # ScAddr(...)
water = generate_link("water", link_type=sc_type.VAR_NODE_LINK)  # ScAddr(...)
names = generate_links("Sam", "Pit")  # [ScAddr(...), ScAddr(...)]
```

### Relations generating

Generate different binary relations with these functions:

```python
def generate_binary_relation(connector_type: ScType, src: ScAddr, trg: ScAddr, *relations: ScAddr) -> ScAddr: ...


def generate_role_relation(src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> ScAddr: ...


def generate_non_role_relation(src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> ScAddr: ...
```

These methods return ScAddr of sc-arc generated between `src` and `trg` sc-elements. 

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.utils import generate_node, generate_nodes
from sc_kpm.utils import generate_binary_relation, generate_role_relation, generate_non_role_relation

src, trg = generate_nodes(*[sc_type.CONST_NODE] * 2)
increase_relation = generate_node(sc_type.CONST_NODE_CLASS)

brel = generate_binary_relation(sc_type.CONST_PERM_POS_ARC, src, trg, increase_relation)  # ScAddr(...)
rrel = generate_role_relation(src, trg, ScKeynodes.rrel_index(1))  # ScAddr(...)
nrel = generate_non_role_relation(src, trg, generate_node(sc_type.CONST_NODE_NON_ROLE))  # ScAddr(...)
```

### Erasing utils

If you want to erase all connectors between two elements, which define by their type use

```python
def erase_connectors(source: ScAddr, target: ScAddr, *connector_types: ScType) -> bool: ...
```

It return **True** if operations was successful and **False** otherwise.

```python
from sc_client.constants import sc_type
from sc_kpm.utils import generate_nodes, generate_connector
from sc_kpm.utils import erase_connectors

src, trg = generate_nodes(*[sc_type.CONST_NODE] * 2)
connector = generate_connector(sc_type.CONST_PERM_POS_ARC, src, trg)
erase_connectors(src, trg, sc_type.CONST_PERM_POS_ARC)  # True
```

### Searching connectors

For getting connector or connectors between two elements use:

```python
def search_connector(source: ScAddr, target: ScAddr, connector_type: ScType) -> ScAddr: ...


def search_connectors(source: ScAddr, target: ScAddr, *connector_types: ScType) -> List[ScAddr]: ...
```

_**NOTE: Use VAR type instead of CONST in getting utils**_

```python
from sc_client.constants import sc_type
from sc_kpm.utils import generate_nodes, generate_connector
from sc_kpm.utils import search_connector, search_connectors

src, trg = generate_nodes(*[sc_type.CONST_NODE] * 2)
connector1 = generate_connector(sc_type.CONST_PERM_POS_ARC, src, trg)
connector2 = generate_connector(sc_type.CONST_COMMON_ARC, src, trg)

class_connector = search_connector(src, trg, sc_type.VAR_PERM_POS_ARC)  # ScAddr(...)
assert class_connector == connector1
connectors = search_connectors(src, trg, sc_type.VAR_PERM_POS_ARC, sc_type.VAR_COMMON_ARC)  # [ScAddr(...), ScAddr(...)]
assert connectors == [connector1, connector2]
```

### Searching elements by relation

Search target element by source element and relation:

```python
def search_element_by_role_relation(src: ScAddr, rrel_node: ScAddr) -> ScAddr: ...


def search_element_by_non_role_relation(src: ScAddr, nrel_node: ScAddr) -> ScAddr: ...
```

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.utils import generate_nodes, generate_role_relation, generate_non_role_relation
from sc_kpm.utils import search_element_by_role_relation, search_element_by_non_role_relation

src, trg_rrel, trg_nrel = generate_nodes(*[sc_type.CONST_NODE] * 3)
rrel = generate_role_relation(src, trg_rrel, ScKeynodes.rrel_index(1))  # ScAddr(...)
nrel = generate_non_role_relation(src, trg_nrel, ScKeynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER])  # ScAddr(...)

result_rrel = search_element_by_role_relation(src, ScKeynodes.rrel_index(1))  # ScAddr(...)
assert result_rrel == trg_rrel
result_nrel = search_element_by_non_role_relation(src, ScKeynodes[CommonIdentifiers.NREL_SYSTEM_IDENTIFIER])  # ScAddr(...)
assert result_nrel == trg_nrel
```

### Getting link content

For existed links you may get their content by address with this function:

```python
def get_link_content(link: ScAddr) -> Union[str, int]: ...
```

```python
from sc_kpm.utils import generate_link
from sc_kpm.utils import get_link_content_data

water = generate_link("water")
content = get_link_content_data(water)  # "water"
```

### Getting element system identifier

For getting system identifier of keynode use:

```python
def get_element_system_identifier(addr: ScAddr) -> str: ...
```

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_element_system_identifier

idtf = get_element_system_identifier(some_addr)  # "lang_en"
```

## Action utils

Utils to work with actions, events and agents

![agent_base](docs/schemes/png/agent_base.png)

### Check action class

```python
def check_action_class(action_class: Union[ScAddr, Idtf], action_node: ScAddr) -> bool: ...
```

This function returns **True** if action class has connection to action node.
You can use identifier of action class instead of ScAddr.
This function should not be used in the ScAgentClassic.

![check action class](docs/schemes/png/check_action_class.png)

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.utils import generate_node, generate_connector
from sc_kpm.utils.action_utils import check_action_class

action_node = generate_node(sc_type.CONST_NODE)
generate_connector(sc_type.CONST_PERM_POS_ARC, ScKeynodes[CommonIdentifiers.ACTION], action_node)
action_class = generate_node(sc_type.CONST_NODE_CLASS)
generate_connector(sc_type.CONST_PERM_POS_ARC, action_class, action_node)

assert check_action_class(action_class, action_node)
# or
assert check_action_class("some_classification", action_node)
```

### Get action arguments

For getting list of action arguments concatenated by `rrel_[1 -> count]` use:

```python
def get_action_arguments(action_class: Union[ScAddr, Idtf], count: int) -> List[ScAddr]: ...
```

![check action class](docs/schemes/png/get_arguments.png)

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers
from sc_kpm.utils import generate_node, generate_connector, generate_role_relation
from sc_kpm.utils.action_utils import get_action_arguments

action_node = generate_node(sc_type.CONST_NODE)

# Static argument
argument1 = generate_node(sc_type.CONST_NODE)
generate_role_relation(action_node, argument1, ScKeynodes.rrel_index(1))

# Dynamic argument
dynamic_node = generate_node(sc_type.CONST_NODE)
rrel_dynamic_arg = ScKeynodes[CommonIdentifiers.RREL_DYNAMIC_ARGUMENT]
generate_role_relation(action_node, dynamic_node, rrel_dynamic_arg, ScKeynodes.rrel_index(2))
argument2 = generate_node(sc_type.CONST_NODE)
generate_connector(sc_type.CONST_TEMP_POS_ARC, dynamic_node, argument2)

arguments = get_action_arguments(action_node, 2)
assert arguments == [argument1, dynamic_node]
```

### Generate and get action result

```python
def generate_action_result(action_node: ScAddr, *elements: ScAddr) -> None: ...


def get_action_result(action_node: ScAddr) -> ScAddr: ...
```

Generate and get structure with output of action

![agent result](docs/schemes/png/agent_result.png)

```python
from sc_client.constants import sc_type
from sc_kpm.utils import generate_node
from sc_kpm.utils.action_utils import generate_action_result, get_action_result
from sc_kpm.sc_sets import ScStructure

action_node = generate_node(sc_type.CONST_NODE)
result_element = generate_node(sc_type.CONST_NODE)
generate_action_result(action_node, result_element)
result = get_action_result(action_node)
result_elements = ScStructure(result).elements_set
assert result_elements == {result_element}
```

### Call, execute and wait agent

Agent call function: generates **action node** with some arguments, concepts and connects it to the node with initiation identifier.
Returns **action node**

```python
def call_agent(
        arguments: Dict[ScAddr, IsDynamic],
        concepts: List[Idtf],
        initiation: Idtf = ActionStatus.ACTION_INITIATED,
) -> ScAddr: ...
```

Agent wait function: Waits for generation of arc from reaction node for some seconds.
Default reaction_node is `action_finished`.

```python
def wait_agent(seconds: float, action_node: ScAddr, reaction_node: ScAddr = None) -> None: ...
```

Agent execute function: combines two previous functions -- calls, waits and returns action node and **True** if success

```python
def execute_agent(
        arguments: Dict[ScAddr, IsDynamic],
        concepts: List[Idtf],
        initiation: Idtf = ActionStatus.ACTION_INITIATED,
        reaction: Idtf = ActionStatus.ACTION_FINISHED_SUCCESSFULLY,
        wait_time: int = COMMON_WAIT_TIME,  # 5
) -> Tuple[ScAddr, bool]: ...
```


![execute_agent](docs/schemes/png/execute_agent.png)

```python
from sc_client.models import ScLinkContentType
from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers, ActionStatus
from sc_kpm.utils import generate_link
from sc_kpm.utils.action_utils import execute_agent, call_agent, wait_agent

arg1 = generate_link(2, ScLinkContentType.INT)
arg2 = generate_link(3, ScLinkContentType.INT)

kwargs = dict(
    arguments={arg1: False, arg2: False},
    concepts=[CommonIdentifiers.ACTION, "some_class_name"],
)

action = call_agent(**kwargs)  # ScAddr(...)
wait_agent(3, action, ScKeynodes[ActionStatus.ACTION_FINISHED])
# or
action, is_successfully = execute_agent(**kwargs, wait_time=3)  # ScAddr(...), bool
```

### Generate, call and execute action

Functions that allow to generate action and add arguments and call later.

Function that generates action with concepts and return its ScAddr.

```python
def generate_action(*concepts: Idtf) -> ScAddr: ...
```

Function that generates arguments of action

```python
def add_action_arguments(action_node: ScAddr, arguments: Dict[ScAddr, IsDynamic]) -> None: ...
```

Now you can call or execute action.
Action call functions don't return action_node because it's parameter to them.

```python
def call_action(
        action_node: ScAddr, initiation: Idtf = ActionStatus.ACTION_INITIATED
) -> None: ...
```

```python
def execute_action(
        action_node: ScAddr,
        initiation: Idtf = ActionStatus.ACTION_INITIATED,
        reaction: Idtf = ActionStatus.ACTION_FINISHED_SUCCESSFULLY,
        wait_time: float = COMMON_WAIT_TIME,
) -> bool: ...
```

Example:

```python
from sc_client.models import ScLinkContentType
from sc_kpm import ScKeynodes
from sc_kpm.identifiers import CommonIdentifiers, ActionStatus
from sc_kpm.utils import generate_link
from sc_kpm.utils.action_utils import add_action_arguments, call_action, generate_action, execute_action, wait_agent

arg1 = generate_link(2, ScLinkContentType.INT)
arg2 = generate_link(3, ScLinkContentType.INT)

action_node = generate_action(CommonIdentifiers.ACTION, "some_class_name")  # ScAddr(...)
# Do something here
arguments = {arg1: False, arg2: False}

add_action_arguments(action_node, arguments)
call_action(action_node)
wait_agent(3, action_node, ScKeynodes[ActionStatus.ACTION_FINISHED])
# or
is_successful = execute_action(action_node, wait_time=3)  # bool
```

### Finish action

Function `finish_action` connects status class to action node:

```python
def finish_action(action_node: ScAddr, status: Idtf = ActionStatus.ACTION_FINISHED) -> ScAddr: ...
```

Function `finish_action_with_status` connects `action_finished` and `action_finished_(un)successfully` statuses to it:

```python
def finish_action_with_status(action_node: ScAddr, is_success: bool = True) -> None: ...
```

![finish_action](docs/schemes/png/finish_action.png)

```python
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.identifiers import ActionStatus
from sc_kpm.utils import generate_node, check_connector
from sc_kpm.utils.action_utils import finish_action, finish_action_with_status

action_node = generate_node(sc_type.CONST_NODE)

finish_action_with_status(action_node)
# or
finish_action_with_status(action_node, True)
# or
finish_action(action_node, ActionStatus.ACTION_FINISHED)
finish_action(action_node, ActionStatus.ACTION_FINISHED_SUCCESSFULLY)

action_finished = ScKeynodes[ActionStatus.ACTION_FINISHED]
action_finished_successfully = ScKeynodes[ActionStatus.ACTION_FINISHED_SUCCESSFULLY]
assert check_connector(sc_type.VAR_PERM_POS_ARC, action_finished, action_node)
assert check_connector(sc_type.VAR_PERM_POS_ARC, action_finished_successfully, action_node)
```

# Use-cases

- Script for generating and registration agent until user press ^C:
    - [based on ScAgentClassic](docs/examples/register_and_wait_for_user.py)
- Scripts for generating agent to calculate sum of two arguments and confirm result:
    - [based on ScAgent](docs/examples/sum_agent.py)
    - [based on ScAgentClassic](docs/examples/sum_agent_classic.py)
- Logging examples:
    - [pretty project logging](docs/examples/pretty_logging.py)
