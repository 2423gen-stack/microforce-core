import asyncio
import pytest
import src.database.queue_worker as qw

# A simple task that takes time to execute to simulate concurrency/queue delays
async def slow_write(value: int):
    await asyncio.sleep(0.1)
    return value * 2

@pytest.mark.asyncio
async def test_graceful_shutdown():
    print("\n--- Starting test_graceful_shutdown ---")
    
    # Save original queue
    original_queue = qw.db_write_queue
    # Create isolated queue for this test
    qw.db_write_queue = asyncio.Queue()
    qw._is_shutting_down = False
    
    try:
        # Start the worker
        print("Starting worker task...")
        worker_task = asyncio.create_task(qw.queue_worker())
        
        # Enqueue a few tasks
        print("Enqueueing tasks...")
        f1 = asyncio.create_task(qw.enqueue_write_operation(slow_write, 10))
        f2 = asyncio.create_task(qw.enqueue_write_operation(slow_write, 20))
        
        # Let them register in the queue
        await asyncio.sleep(0.01)
        
        # Trigger shutdown while tasks are in progress
        print("Triggering stop_queue_worker...")
        await qw.stop_queue_worker()
        print("stop_queue_worker completed.")
        
        # Check that both tasks completed successfully and yielded correct values
        print("Awaiting task futures...")
        v1 = await f1
        v2 = await f2
        print(f"v1={v1}, v2={v2}")
        assert v1 == 20
        assert v2 == 40
        
        # Verify that trying to enqueue a new task now raises RuntimeError
        print("Testing enqueue after shutdown...")
        with pytest.raises(RuntimeError) as excinfo:
            await qw.enqueue_write_operation(slow_write, 30)
        assert "shutting down" in str(excinfo.value)
        
        # Clean up worker task (should have terminated because of sentinel)
        print("Awaiting worker_task...")
        await worker_task
        print("Test complete.")
    finally:
        # Restore the original queue and state
        qw.db_write_queue = original_queue
        qw._is_shutting_down = False
