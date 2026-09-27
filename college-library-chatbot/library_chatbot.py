import sys
import json
import re

# Fix Windows terminal encoding
sys.stdout.reconfigure(encoding="utf-8")


# -----------------------------------------
# Load Library Books
# -----------------------------------------

with open("books.json", "r", encoding="utf-8") as file:
    books = json.load(file)


# -----------------------------------------
# Common Words to Ignore
# -----------------------------------------

STOP_WORDS = {
    "do", "you", "have", "any", "books", "book",
    "on", "about", "the", "a", "an", "is", "are",
    "available", "availability", "show", "me",
    "what", "which", "can", "i", "find", "for",
    "in", "of", "to", "please", "give", "list",
    "all", "there", "some", "with", "who", "wrote",
    "by", "tell", "does", "your", "library"
}


# -----------------------------------------
# Extract Useful Keywords
# -----------------------------------------

def get_keywords(question):

    # Convert to lowercase
    question = question.lower()

    # Remove punctuation
    question = re.sub(r"[^a-zA-Z0-9\s]", "", question)

    # Split into words
    words = question.split()

    # Remove common words
    keywords = [
        word for word in words
        if word not in STOP_WORDS
    ]

    return keywords


# -----------------------------------------
# Search Books
# -----------------------------------------

def search_books(question):

    keywords = get_keywords(question)

    results = []

    for book in books:

        title = book["title"].lower()
        author = book["author"].lower()
        category = book["category"].lower()

        # Check whether any useful keyword matches
        for keyword in keywords:

            if (
                keyword in title
                or keyword in author
                or keyword in category
            ):
                results.append(book)
                break

    return results


# -----------------------------------------
# Display Book Information
# -----------------------------------------

def format_book(book):

    status = (
        "Available"
        if book["available"]
        else "Currently issued"
    )

    return (
        f"📖 {book['title']}\n"
        f"   Author: {book['author']}\n"
        f"   Category: {book['category']}\n"
        f"   Year: {book['year']}\n"
        f"   Status: {status}"
    )


# -----------------------------------------
# Chatbot
# -----------------------------------------

def chatbot(question):

    original_question = question
    question = question.lower().strip()

    # -----------------------------------------
    # Exit
    # -----------------------------------------

    if question in ["exit", "quit", "bye"]:

        return "Goodbye! 👋"


    # -----------------------------------------
    # Show All Books
    # -----------------------------------------

    if (
        "all books" in question
        or "list books" in question
        or question == "books"
        or "list all" in question
    ):

        answer = "📚 Books available in the library:\n\n"

        for book in books:
            answer += format_book(book) + "\n\n"

        return answer


    # -----------------------------------------
    # Search Books
    # -----------------------------------------

    results = search_books(original_question)


    # -----------------------------------------
    # No Results
    # -----------------------------------------

    if not results:

        return (
            "Sorry, I couldn't find a matching book. 😕\n\n"
            "Try asking something like:\n"
            "• Do you have Python books?\n"
            "• Books on machine learning\n"
            "• Who wrote Clean Code?\n"
            "• Is Atomic Habits available?\n"
            "• Books by James Clear"
        )


    # -----------------------------------------
    # Author Question
    # -----------------------------------------

    if (
        "who wrote" in question
        or "author" in question
        or "written by" in question
        or "by " in question
    ):

        answer = ""

        for book in results:

            answer += (
                f"📖 {book['title']}\n"
                f"   Author: {book['author']}\n\n"
            )

        return answer


    # -----------------------------------------
    # Availability Question
    # -----------------------------------------

    if (
        "available" in question
        or "availability" in question
        or "can i borrow" in question
    ):

        answer = ""

        for book in results:

            if book["available"]:
                status = "✅ Available"
            else:
                status = "❌ Currently issued"

            answer += (
                f"📖 {book['title']}\n"
                f"   Author: {book['author']}\n"
                f"   Status: {status}\n\n"
            )

        return answer


    # -----------------------------------------
    # General Search
    # -----------------------------------------

    answer = "🔎 I found these books:\n\n"

    for book in results:

        answer += format_book(book) + "\n\n"

    return answer


# -----------------------------------------
# Main Program
# -----------------------------------------

print("=" * 60)
print("              📚 COLLEGE LIBRARY CHATBOT")
print("=" * 60)

print("\nBot: Hello! 👋")
print("Bot: I can help you find books in the college library.")
print()
print("Bot: You can ask about:")
print("     • Book titles")
print("     • Authors")
print("     • Categories")
print("     • Availability")
print()
print("Bot: Type 'exit' to quit.\n")


# -----------------------------------------
# Chat Loop
# -----------------------------------------

while True:

    question = input("You: ")

    response = chatbot(question)

    print(f"\nBot: {response}")

    if question.lower().strip() in ["exit", "quit", "bye"]:
        break

    print()