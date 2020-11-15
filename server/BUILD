py_binary(
    name = "server",
    main = "main.py",
    python_version = "PY3",
    srcs = [
        "main.py",
        "cards.py",
    ],
    #deps = [
    #    "@rules_python//python/runfiles",
    #],
    data = [
        ":templates/index.html",
        ":templates/room.html",
    ]
)


