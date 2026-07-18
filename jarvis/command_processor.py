from helpers import safe_print

from ai.classifier import (
    classify,
    PRIORITY_LOCAL,
)

from dispatcher import (
    dispatch,
    execute_direct,
)

# ============================================================
# Command Processing
# ============================================================

def split_commands(query: str):

    if " and " in query:

        return [

            item.strip()

            for item in query.split(" and ")

            if item.strip()

        ]

    if "." in query:

        return [

            item.strip()

            for item in query.split(".")

            if item.strip()

        ]

    return [

        query.strip()

    ]


def handle_command(

    scheduler,

    query

):

    query = query.strip()

    if not query:

        return

    safe_print(

        f"[dispatch] {query}"

    )

    commands = split_commands(query)

    classified = []

    for command in commands:

        priority, kind, payload = classify(command)

        classified.append(

            (

                priority,

                kind,

                payload,

                command

            )

        )

    tasks = [

        task

        for task in classified

        if task[1] != "noop"

    ]

    if not tasks:

        return

    if len(tasks) == 1:

        priority, kind, payload, command = tasks[0]

        execute_direct(

            scheduler,

            kind,

            payload,

            command

        )

        return

    simple = [

        task

        for task in tasks

        if task[0] == PRIORITY_LOCAL

    ]

    complex_tasks = sorted(

        [

            task

            for task in tasks

            if task[0] != PRIORITY_LOCAL

        ],

        key=lambda x: x[0]

    )

    for priority, kind, payload, command in simple + complex_tasks:

        dispatch(

            scheduler,

            priority,

            kind,

            payload,

            command

        )
