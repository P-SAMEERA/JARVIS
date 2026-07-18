from tasks import (
    task_open_url,
    task_screenshot,
    task_time,
    task_exit,
    task_bye,
    task_system_operation,
    task_self_description,
    task_code,
    task_general,
    task_agent,
)

# ============================================================
# Dispatcher
# ============================================================

def get_task(

    scheduler,

    kind,

    payload,

    query

):

    mapping = {

        "open": (

            task_open_url,

            (scheduler, payload)

        ),

        "screenshot": (

            task_screenshot,

            (scheduler,)

        ),

        "time": (

            task_time,

            (scheduler,)

        ),

        "exit": (

            task_exit,

            (scheduler,)

        ),

        "bye": (

            task_bye,

            (scheduler,)

        ),

        "E": (

            task_system_operation,

            (scheduler, query)

        ),

        "D": (

            task_self_description,

            (scheduler,)

        ),

        "Y": (

            task_code,

            (scheduler, query)

        ),

        "N": (

            task_general,

            (scheduler, query)

        ),

        "A": (

            task_agent,

            (scheduler, query)

        )

    }

    return mapping.get(kind)


def dispatch(

    scheduler,

    priority,

    kind,

    payload,

    query

):

    task = get_task(

        scheduler,

        kind,

        payload,

        query

    )

    if task is None:

        return

    function, args = task

    scheduler.submit(

        priority,

        function,

        *args

    )


def execute_direct(

    scheduler,

    kind,

    payload,

    query

):

    task = get_task(

        scheduler,

        kind,

        payload,

        query

    )

    if task is None:

        return

    function, args = task

    scheduler.run_now(

        function,

        *args

    )