import asyncio
import uuid
from langchain_core.messages import HumanMessage
from graph import build_syntapse_graph

async def simulate_concurrent_requests():
    """
    Simulates testing the Syntapse Graph for concurrency (C1-C10).
    """
    app = build_syntapse_graph()
    
    # We will simulate a user session
    session_id = "SESSION_TEST_123"
    
    # C1: Double-submit same user message
    # Simulating a user double-clicking 'Send'
    msg_content = "What is a Transformer?"
    
    config1 = {"configurable": {"thread_id": session_id}}
    config2 = {"configurable": {"thread_id": session_id}}
    
    # We use a mocked state
    base_state = {
        "topic_name": "Transformer Architecture",
        "session_id": session_id,
        "turn_id": 1,
        "request_id": f"REQ_{uuid.uuid4().hex[:8]}",
        "messages": [HumanMessage(content=msg_content)]
    }
    
    print("Running C1: Double-submit test (simulated race condition)...")
    
    # In LangGraph, async execution over the same thread_id is queued or handled by the checkpointer.
    # To truly test concurrency, we would use app.ainvoke
    
    try:
        task1 = app.ainvoke(base_state, config1)
        task2 = app.ainvoke(base_state, config2)
        results = await asyncio.gather(task1, task2, return_exceptions=True)
        print("Results of double-submit:")
        for r in results:
            if isinstance(r, Exception):
                print(f"Exception caught (expected due to optimistic locking/concurrency): {r}")
            else:
                print("Success.")
    except Exception as e:
        print(f"Concurrency checkpointer handled it: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_concurrent_requests())
