class ErrorDefaultMessages:
    """Common description of exceptions"""

    INVALID_STATE = "Invalid state"
    INVALID_VALUE = "Invalid value"
    INVALID_TYPE = "Invalid type"
    MERGE_ERROR = "You can't merge two different syntax types"
    LINK_OVERSIZE = "Link content exceeds permitted value"
    SERVER_ERROR = "Server error"
    PAYLOAD_MAX_SIZE = "Payload max size error"


class ErrorNotes:
    """Exception notes that go after default messages"""

    IntTypeInitialization = "You must use int type for initialization"
