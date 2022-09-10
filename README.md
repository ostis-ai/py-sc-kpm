# py-sc-kpm
The python implementation of the knowledge processing machine (kpm) for [sc-machine](https://github.com/ostis-ai/sc-machine).
Library provides tools for interacting with knowledge bases.
Communication with server is implemented in separate library named [py-sc-client](https://github.com/ostis-ai/py-sc-client).
This module is compatible with 0.7.0 version of [OSTIS Technology platform](https://github.com/ostis-ai/ostis-web-platform).

#API Reference

## Classes
The library contains the python implementation of useful classes and functions to work with the sc-memory.

There is a list of classes:

 - ScKeynodes
 - ScAgent
 - ScModule
 - ScServer


### ScKeynodes
A singleton dictionary object which provides the ability to cache the identifier and ScAddr of keynodes stored in the KB.
Create an instance of the ScKeynodes class to get access to the cache:

```py
from sc_kpm import ScKeynodes
keynodes = ScKeynodes()
```

Get the provided identifier:
```py
keynodes["identifier_of_keynode"] # returns an ScAddr of the given identifier
keynodes["not_stored_in_kb"] # returns an invalid ScAddr if an identifier does not exist in the memory
```

Use _resolve()_ method to resolve identifiers:

```py
my_class_node = keynodes.resolve("my_class_node", sc_types.NODE_CONST_CLASS)
```


### ScAgent
A class for handling a single ScEvent. Define your agents like this:
```py
from sc_kpm import ScAgent

class ScAgentTest(ScAgent):
    def on_event(self, _src, _edge, target_node) -> ScResult:
        logger.info(f"{ScAgentTest.__name__} is started")
        ...
        return ScResult.OK
```


### ScModule
A class for registrating and handling multiple ScAgent objects. Define your modules like this:
```py
from sc_kpm import ScModule

class ScModuleTest(ScModule):
    agents = [
        ScAgentTest(source_node=test_node_idtf, event_type=ScEventType.ADD_OUTGOING_EDGE),
        ...
    ]
```


### ScServer
A class for serving ScModule objects. Initialize and run server like this:
```py
from sc_kpm import ScServer

SC_SERVER_URL = "ws://localhost:8090/ws_json"
server = ScServer(SC_SERVER_URL)
server.start()
...
```

You can regiter your modules wherever you want. Manage your modules like this:
```
module = ScModuleTest()
server.add_modules(module)
...
server.remove_modules(module)
...
```

After stopping server, all modules and agents will be deactivated.
```
server.stop()
...
```

## Utils
...
