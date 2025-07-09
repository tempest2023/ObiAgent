# Code Refactor Task 1
Move all shared keys to an enum class, like `shared["summary"]` should be `shared[SharedKeys.SUMMARY]` and update all shared operations to use this enum class


# Code Refactor Task 2
Move all websocket operations to a separate class, like `WebSocketManager` and update all websocket operations to use this class.
Manage all websocket message types in an enum class `WebSocketMessageType` and update all websocket message type to use this enum class.



