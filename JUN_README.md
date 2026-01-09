# How to Communicate with the ADK API Server

This guide explains how your frontend application can communicate with the locally hosted ADK API server (default port `8000`).

## Base URL
The default base URL for the local API server is:
`http://localhost:8000`

## 1. Create a Session
Before sending queries, you should create a session. A session maintains the conversation history and state for a user.

*   **Endpoint:** `POST /apps/{agent_name}/users/{user_id}/sessions/{session_id}`
*   **Description:** Creates a new session or resets an existing one.
*   **Parameters:**
    *   `agent_name`: The name of your agent (e.g., `my_agent`).
    *   `user_id`: A unique identifier for the user (e.g., `1`).
    *   `session_id`: A unique identifier for the session (e.g., `s-1`).

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/apps/my_agent/users/1/sessions/s-1" \
     -H "Content-Type: application/json" \
     -d '{}'
```

**JavaScript Example (Fetch API):**
```javascript
const agentName = "my_agent";
const userId = "1";
const sessionId = "s-1";

async function createSession() {
  const response = await fetch(`http://localhost:8000/apps/${agentName}/users/${userId}/sessions/${sessionId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({}) // Optional: Initial state can go here
  });

  if (response.ok) {
    console.log("Session created successfully");
  } else {
    console.error("Failed to create session");
  }
}
```

## 2. Send a Query (Run Agent)
Once a session is created, you can send messages to the agent within that session.

*   **Endpoint:** `POST /run` (for single response) or `POST /run_sse` (for streaming response)
*   **Description:** Sends a user message to the agent and executes it.

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/run" \
     -H "Content-Type: application/json" \
     -d '{
           "appName": "my_agent",
           "userId": "1",
           "sessionId": "s-1",
           "newMessage": {
             "role": "user",
             "parts": [{"text": "I want to rent a guitar"}]
           }
         }'
```

**JavaScript Example (Fetch API):**
```javascript
async function sendMessage(text) {
  const response = await fetch("http://localhost:8000/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      appName: "my_agent",
      userId: "1",
      sessionId: "s-1",
      newMessage: {
        role: "user",
        parts: [{ text: text }]
      }
    })
  });

  const data = await response.json();
  console.log("Agent Response:", data);
}
```

---

## FAQ: Session Persistence & Memory

### 1. Is the session saved every time I host the local server?
**No.** By default, the local ADK server uses an **in-memory** implementation for sessions. This means:
*   **When the server is running:** Sessions are active and data is stored in RAM.
*   **When you restart the server:** All sessions, history, and state are **lost**. You must create a new session each time you restart the server.

### 2. Does the conversation have memory in the session?
**Yes.** Within the lifespan of a single session (i.e., while the server is running and the session ID is reused):
*   The agent remembers the history of messages (User and Agent turns).
*   It maintains context (state) across multiple turns.
*   The `Session` object automatically manages this chronological history.

If you change the `sessionId` (or if the server restarts), that "memory" is reset.
