from graph import app
from database import init_db

init_db()

print("Inventory Chatbot Started (type 'exit' to quit)")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    result = app.invoke({
        "user_input": user_input
    })

    print("Bot:", result["result"])