py_binary(
    name = "server",
    main = "main.py",
    python_version = "PY3",
    srcs = [
        "main.py",
    ],
    deps = [
        ":cards",
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
    ]
)

py_library(
    name = "cards",
    srcs = [
        "cards.py",
    ]
)
