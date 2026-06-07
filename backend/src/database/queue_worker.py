import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

# The global queue for all database write operations
db_write_queue: asyncio.Queue = asyncio.Queue()
_is_shutting_down = False

async def queue_worker():
    """
    A background worker that processes database write requests sequentially.
    This prevents 'database is locked' errors in SQLite by ensuring
    only one transaction writes at a time.
    """
    logger.info("Database queue worker started.")
    while True:
        task = await db_write_queue.get()
        if task is None:
            logger.info("Database queue worker received shutdown sentinel.")
            db_write_queue.task_done()
            break
            
        func = task.get("func")
        args = task.get("args", ())
        kwargs = task.get("kwargs", {})
        future = task.get("future")

        try:
            # Execute the database operation
            result = await func(*args, **kwargs)
            if future and not future.done():
                future.set_result(result)
        except Exception as e:
            logger.error(f"Error in queue worker executing {func.__name__}: {e}")
            if future and not future.done():
                future.set_exception(e)
        finally:
            db_write_queue.task_done()

async def enqueue_write_operation(func: Callable, *args, **kwargs) -> Any:
    """
    Enqueue a database write operation and wait for its result.
    """
    if _is_shutting_down:
        raise RuntimeError("Database queue worker is shutting down. Write operations are disabled.")

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    
    await db_write_queue.put({
        "func": func,
        "args": args,
        "kwargs": kwargs,
        "future": future
    })
    
    # Wait for the worker to process this task and return the result
    return await future

async def stop_queue_worker():
    """
    Gracefully signals the worker to stop and waits for all pending tasks to complete.
    """
    global _is_shutting_down
    if _is_shutting_down:
        return
    _is_shutting_down = True
    logger.info("Signaling database queue worker to stop...")
    await db_write_queue.put(None)
    await db_write_queue.join()
    logger.info("Database queue worker stopped gracefully.")

