py_binary(
    name = "server",
    main = "main.py",
    python_version = "PY3",
    srcs = [
        "main.py",
    ],
    deps = [
        ":rooms",
    ],
    data = [
        ":templates/index.html",
        ":templates/room.html",
    ]
)

py_library(
    name = "rooms",
    srcs = [
        "rooms.py",
    ],
    deps = [
        ":constants",
        ":deck",
    ]
)

py_library(
    name = "deck",
    srcs = [
        "deck.py",
    ],
    deps = [
        ":constants",
    ]
)

py_library(
    name = "constants",
    srcs = [
        "constants.py",
    ]
)
