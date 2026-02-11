import os
from core.utils import ask_ai, process_and_execute

# Plugin Configuration
config = {
    "label": "Agent Mode (Total control)", 
    "icon": "🧠"
}

def run():
    """
    Executes the autonomous agent mode. 
    The agent can perform system tasks using Python scripts.
    """
    os.system('clear')
    print("=== 🧠 AGENT MODE (TOTAL CONTROL) ===")
    print("Type your command or task for the system (e.g., 'Clean temp files', 'Organize my apps')")
    
    order = input("\n👉 Command: ").strip()
    
    if not order or order == "0":
        return

    # System prompt optimized for English output and Termux environment
    sys_prompt = (
        "You are an Expert Termux System Agent. "
        "Your goal is to fulfill the user's request by writing a Python script. "
        "Strictly follow this format: "
        "1. Start with ---CODIGO--- followed by the raw Python code. "
        "2. End with ---SUGERENCIA--- followed by a brief explanation or next step. "
        "All code, comments, and messages MUST be in English."
    )
    
    print("\n🧠 Agent is thinking...")
    
    # Request logic from AI
    response = ask_ai(order, sys_prompt)
    
    if response:
        # process_and_execute handles the parsing and execution of the script
        process_and_execute(response, "agent_task")
    else:
        print("❌ Error: Could not get a response from the AI.")
        input("\nPress Enter to return...")

if __name__ == "__main__":
    run()