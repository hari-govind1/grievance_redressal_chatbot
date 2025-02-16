from flask import Flask, render_template, request, redirect, url_for, flash
import openai
import openaiAPIkey
import grievance_handler  # Assuming this is your local module
import database_handler  # Assuming this is your local module
from pdf_processing import extract_text_from_pdf, split_text_into_chunks  # Assuming this is your local module
from embedding import generate_embeddings  # Assuming this is your local module
from vector_store import VectorStore  # Assuming this is your local module
from search import search_query  # Assuming this is your local module
from llm import generate_response  # Assuming this is your local module

app = Flask(__name__)
app.secret_key = "5d0588a1403b7b871788c1de0dbf68055b6488df092faf5961fff33da71df2f6"  # Important for flash messages

# Load OpenAI API key
openai.api_key = openaiAPIkey.open_ai_api_key

# ... (DEPARTMENTS list remains the same)
DEPARTMENTS = [
    "Academic Department", "Administrative Department", "Hostel Department",
    "Library Department", "Cafeteria Department", "Placement Department",
    "Technical Support Department", "Transportation Department", "Electrical Maintenance Department"
]

# ... (All the helper functions like verify_legitimacy, is_meaningful_grievance, classify_with_openai remain the same)
def verify_legitimacy(name, user_class, user_department, grievance_text, location):
    """Verify if the grievance details are legitimate using ChatGPT."""
    prompt = f"""
    Verify if the following grievance details are legitimate. Ensure the name is valid, 
    class and department are valid. Respond only with:
    - 'Legitimate' (if valid)
    - 'Not Legitimate' (if invalid)

    Name: {name}
    Class: {user_class}
    Department: {user_department}
    Grievance: {grievance_text}
    Location: {location}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5
    )

    return response["choices"][0]["message"]["content"].strip()


def is_meaningful_grievance(grievance_text):
    """Uses GPT-4o Mini to check if the grievance is meaningful."""
    prompt = f"""
    Determine if the following grievance is meaningful and relevant to a college grievance redressal system.
    Respond only with:
    - 'Valid' (if the grievance is meaningful)
    - 'Invalid' (if it is gibberish, irrelevant, or too vague)

    Grievance: "{grievance_text}"
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "You check whether grievances are meaningful for a college redressal system."},
            {"role": "user", "content": prompt.strip()}
        ],
        max_tokens=5  # Ensures a short response
    )
    
    return response["choices"][0]["message"]["content"].strip()

def classify_with_openai(grievance_text, assigned_departments):
    """Uses GPT-4o Mini to verify grievance classification against a fixed department list."""
    prompt = f"""
    A grievance has been classified into a department. Your task is to verify if the classification is correct. 
    Choose only from the given department list. Respond strictly in this format:
    'Correct: Yes' (if correct) OR 'Correct: No, Suggested Department: [Department Name]'.

    Grievance: "{grievance_text}"
    Assigned Departments: "{', '.join(assigned_departments)}"
    Choose from: {", ".join(DEPARTMENTS)}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "You are an AI that verifies grievance classification using a fixed department list."},
            {"role": "user", "content": prompt.strip()}
        ],
        max_tokens=15  # Keeps response short
    )
    
    return response["choices"][0]["message"]["content"]


# Initialize Vector Store (do this ONCE when the app starts)
PDF_PATH = "D:\Chat-Bot-Project-main\data\KIT Rules and regulation.pdf" # Make sure path is correct
try:
    text = extract_text_from_pdf(PDF_PATH)
    chunks = split_text_into_chunks(text)
    embeddings = generate_embeddings(chunks)
    vector_store = VectorStore(dimension=len(embeddings[0]))
    vector_store.add_documents(chunks, embeddings)
except Exception as e: # Handle potential file errors
    print(f"Error initializing vector store: {e}")
    exit() # Exit the application if vector store cannot be initialized


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        choice = request.form.get("choice")

        if choice == "1":
            return redirect(url_for("qa_bot"))
        elif choice == "2":
            return redirect(url_for("grievance"))
        elif choice == "3":
            return "Thank you for using the Grievance Redressal Bot. Goodbye! 👋"  # Just return a string for now
        else:
            flash("Invalid choice. Please select a valid option.")
            return redirect(url_for("index"))

    return render_template("index.html")  # Create index.html



@app.route("/qa_bot", methods=["GET", "POST"])
def qa_bot():
    answer = None
    if request.method == "POST":
        query = request.form.get("query")
        if query.lower() == "exit":
            return redirect(url_for("index"))  # Redirect to the main menu

        if query:
            retrieved_text = search_query(query, vector_store)
            answer = generate_response(query, retrieved_text)
        else:
            flash("Please enter a valid question.")

    return render_template("qa_bot.html", answer=answer) # Create qa_bot.html


@app.route("/grievance", methods=["GET", "POST"])
def grievance():
    if request.method == "POST":
        grievance_text = request.form.get("grievance")
        name = request.form.get("name")
        user_class = request.form.get("user_class")
        user_department = request.form.get("user_department")
        location = request.form.get("location")
        email = request.form.get("email")
        additional_comments = request.form.get("additional_comments")

        validation_result = is_meaningful_grievance(grievance_text)
        if validation_result != "Valid":
            flash("⚠️ Invalid grievance. Please enter a meaningful grievance.")
            return redirect(url_for("grievance"))

        assigned_departments = grievance_handler.handle_grievance(grievance_text)
        verification_result = classify_with_openai(grievance_text, assigned_departments)

        suggested_department = None
        if "Correct: No" in verification_result:
            suggested_department = verification_result.split("Suggested Department:")[-1].strip()

        if "Correct: No" in verification_result:
            flash("The grievance classification needs refinement. Please provide more details.")
            return redirect(url_for("grievance")) # Re-render the form

        legitimacy = verify_legitimacy(name, user_class, user_department, grievance_text, location)
        if legitimacy != "Legitimate":
            flash("⚠️ Grievance details are not legitimate.")
            return redirect(url_for("grievance"))

        summary_prompt = f"Summarize the following grievance in 20 words or less:\n\nGrievance: {grievance_text}"
        summary_response = openai.ChatCompletion.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=20
        )
        summary = summary_response["choices"][0]["message"]["content"].strip()

        # ... (Store in Database)
        for department in assigned_departments: #or final_department, depending on your logic
            database_handler.store_grievance(
                department, name, user_class, user_department, location, email, summary, additional_comments
            )

        flash("✅ Grievance submitted successfully and stored in the database.")
        return redirect(url_for("index"))  # Redirect back to the main menu

    return render_template("grievance.html") # Create grievance.html


if __name__ == "__main__":
    app.run(debug=True)