# Code-Review-Assistant

![Code-Review-Assistant](https://github.com/user-attachments/assets/d3b66c82-867b-49f1-be56-a57a5930fa0a)

A VS Code extension for line-level code review with severity highlights.  
It submits code to a backend, gets AI-generated feedback, and visually annotates your code.

## Setup & Usage

Follow these steps to run the Code-Review-Assistant:

1. **Start Redis**  
   Open a terminal and run: docker run -p 6379:6379 redis

2. **Run the Backend**
   In a second terminal: python -m backend.app

3. **Start the Worker**
   In a third terminal: python -m backend.worker_windows

4. **Compile the VS Code Extension**
   In a fourth terminal: npm run compile

5. **Run the Extension**
   Press `Ctrl + F5` in VS Code to launch the extension in a new window.

6. **Review Your Code**
   - Open the file you want to review.
   - Run the command: **Run Code Review** (from Command Palette or keyboard shortcut).

## Results

- The extension submits the code to the backend and displays the **submission ID** in the bottom panel.
- Code lines are highlighted according to severity.
- Hovering over a highlighted line shows the **feedback** with explanation.

## Troubleshooting

- Ensure **Redis** is running before starting the backend.
- Backend must be running at `http://localhost:5000`.
- Worker must be active to process queued code submissions.
- Compile the extension (`npm run compile`) before running in VS Code.
- If feedback doesn’t appear, check console logs for backend or worker errors.

## Tech Stack

- **VS Code Extension**: TypeScript, VS Code API
- **Backend**: Python, Flask, RQ (Redis Queue)
- **AI Feedback**: Mistral via OpenRouter API
- **Database**: SQLite for storing submissions and feedback, faiss for storing embeddings
