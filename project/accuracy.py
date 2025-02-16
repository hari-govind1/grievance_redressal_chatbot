import openai
import chromadb
import os

# Set your OpenAI API key
openai.api_key = " "
# Initialize Chroma client
client = chromadb.PersistentClient(path="D:/New folder1")

# Create a collection in Chroma
collection = client.get_collection('grievance_data')

# Function to get embeddings from OpenAI
def get_embeddings(text: str):
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return response['data'][0]['embedding']


# Function to query the ChromaDB with a text and retrieve similar documents
def query_chroma(query_text: str, top_k=10):
    departments=[]
    query_embedding = get_embeddings(query_text)
    if query_embedding is None:
        return

    try:
        # Perform the search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Print the department IDs and the corresponding texts of the results
        for i, result in enumerate(results['documents'][0]):  # Access the first query's results
            metadata = results['metadatas'][0][i]  # Access metadata for the current result
            department_id = metadata.get('department_id', 'N/A')  # Use .get() to handle missing keys
            departments.append(department_id)
            #print(f"Result {i + 1}: Department ID: {department_id}")#add , Grievance: {result} along with the department_id if we want the entire grievance
        return departments
    except Exception as e:
        print(f"Error querying Chroma DB: {e}")

# Example query
#print("enter the grievance that you have with college(only one grievance at a time)")

def get_grievance_department(query_text):
    top_ten_departments=query_chroma(query_text)
    #creating dictionary with sll the departement with default value as 0
    keys = ['Academic department','Administrative department','Hostel Department','Library Department','Cafeteria Department','Placement Department','Technical Support Department','Transportation Department','Electrical Maintenance Department']
    default_value = 0
    top_ten_departments_count = dict.fromkeys(keys, default_value)
    for i in top_ten_departments:
        top_ten_departments_count[i] += 1

    top_ten_departments_count_desc = dict(sorted(top_ten_departments_count.items(), key=lambda item: item[1], reverse=True))

    #print(top_ten_departments_count_desc)
    iterator = iter(top_ten_departments_count_desc.items())
    first_key, first_value = next(iterator)
    second_key, second_value = next(iterator)

    if(first_value > second_value):#the top similar department
        #print("Grievance department is:",first_key)
         predicted_department = first_key
    if(first_value == second_value): # the grievance may be related to both departments
        #print(f"The grievance may be fits or second department: {first_key} or {second_key}")
        predicted_department = [first_key, second_key]
    #print(predicted_department)

    return predicted_department
    #print(top_ten_departments)

#print("enter the grievance:")
#query_text = input()
#inserting some random queries for checking accuracy

def calculate_accuracy(predicted_outputs, expected_outputs):
    correct_predictions = 0
    total_predictions = len(expected_outputs)
    for predicted, expected in zip(predicted_outputs, expected_outputs):
        # Convert both to sets
        predicted_set = set(predicted) if isinstance(predicted, list) else {predicted}
        expected_set = set(expected) if isinstance(expected, list) else {expected}

        # Check if all expected departments are in the predicted departments
        if expected_set.issubset(predicted_set):  # This allows extra departments
            correct_predictions += 1

    accuracy = (correct_predictions / total_predictions) * 100
    return accuracy

#main function to check accuracy
grievances_data = [
    "I need clarification on the prerequisites for elective subjects this semester. The academic counselor is unavailable to assist.",
    "The exam results for the previous semester have been delayed by over two weeks. This is affecting my graduation timeline.",
    "The ceiling fan and lights in my hostel room have not been functioning for a week. Multiple complaints have gone unanswered.",
    "Several essential reference books required for project research are missing from the library. They haven't been restocked in months.",
    "The cafeteria consistently serves cold and stale food during dinner. Students are falling sick due to unhygienic conditions.",
    "There has been no notification regarding placement activities or company visits for final-year students. We are feeling left in the dark.",
    "I am unable to access the software tools required for completing my project work. The license seems to have expired.",
    "The bus that covers my route has been irregular for the past few days. I missed my morning classes twice due to this issue.",
    "The course registration portal frequently crashes during peak hours. I could not register for my preferred elective subject.",
    "The administrative department misplaced my fee receipt, and now I am being asked to pay additional fines without valid reason.",
    "There is severe water leakage in the washrooms of my hostel block. The cleaning staff has not addressed this problem yet.",
    "The library's air conditioner has not been functional during exam periods. It becomes difficult to concentrate due to the heat.",
    "The dining area in the cafeteria has not been cleaned thoroughly for weeks. The tables and floors are sticky and dirty.",
    "I need assistance with writing an effective resume for the placement season. The placement coordinator is not responding.",
    "The internet connectivity in the labs is extremely slow. This is affecting my ability to attend online sessions and submit assignments.",
    "The college transport services are unreliable, and buses are frequently late. This makes it difficult for students to reach on time.",
    "I am facing difficulties understanding the grading criteria for the term project. My professor is not providing any clarification.",
    "The timetable for the semester has not been updated on the academic portal, causing confusion among students.",
    "The hostel bathrooms have poor drainage, leading to frequent water blockages and foul smells.",
    "The library's digital catalog is often unresponsive, making it difficult to locate books and resources.",
    "The cafeteria frequently runs out of vegetarian meal options during lunch hours, leaving limited choices for students.",
    "There is no information available regarding internships or training programs for pre-final year students.",
    "The college website is down, preventing students from accessing important notices and forms.",
    "The bus route schedules are not updated on the transportation portal, leading to confusion among students.",
    "I was unable to download my hall ticket due to a technical error on the academic portal.",
    "My scholarship application status has been pending for weeks, and the administrative staff is unresponsive.",
    "The hostel common area remains dirty despite multiple complaints to the maintenance team.",
    "The library printers are often out of ink, making it difficult for students to print essential documents.",
    "The cafeteria staff is rude and does not address students' concerns regarding portion sizes or menu changes.",
    "The placement department has not conducted any mock interviews or training sessions this year.",
    "The classroom projectors are not functioning, disrupting lectures and presentations.",
    "The transportation department did not inform us about route changes, causing missed buses.",
    "The subject allocation for elective courses has been mishandled, resulting in incorrect course enrollments.",
    "The administrative department is not processing requests for duplicate ID cards promptly.",
    "There are frequent power outages in the hostel, affecting students' study schedules.",
    "The library seating area is overcrowded, and students often do not find a place to sit.",
    "The cafeteria does not maintain proper food storage conditions, leading to stale food being served.",
    "The placement cell has not shared any information on company eligibility criteria or placement timelines.",
    "I am unable to access the technical support helpline during urgent academic project deadlines.",
    "The transportation department buses are overcrowded, making it unsafe for students to commute.",
    "The exam schedule has been announced late, leaving insufficient time for preparation.",
    "My fee refund request has not been addressed by the administrative office despite multiple follow-ups.",
    "The hostel security staff is not vigilant, leading to unauthorized entry into the premises.",
    "The library Wi-Fi is not working, making it difficult for students to access online resources.",
    "The cafeteria does not provide allergy-safe food options for students with dietary restrictions."
]

expected_outputs = [
    "Academic department",
    "Academic department",
    "Hostel Department",
    "Library Department",
    "Cafeteria Department",
    "Placement Department",
    "Technical Support Department",
    "Transportation Department",
    "Academic department",
    "Administrative department",
    "Hostel Department",
    "Library Department",
    "Cafeteria Department",
    "Placement Department",
    "Technical Support Department",
    "Transportation Department",
    "Academic department",
    "Academic department",
    "Hostel Department",
    "Library Department",
    "Cafeteria Department",
    "Placement Department",
    "Technical Support Department",
    "Transportation Department",
    "Academic department",
    "Administrative department",
    "Hostel Department",
    "Library Department",
    "Cafeteria Department",
    "Placement Department",
    "Technical Support Department",
    "Transportation Department",
    "Academic department",
    "Administrative department",
    "Hostel Department",
    "Library Department",
    "Cafeteria Department",
    "Placement Department",
    "Technical Support Department",
    "Transportation Department",
    "Academic department",
    "Administrative department",
    "Hostel Department",
    "Library Department",
    "Cafeteria Department"
]

predicted_outputs=[]

for grievance in grievances_data:
    predicted_departments = get_grievance_department(grievance)  # Always returns correct format
    predicted_outputs.append(predicted_departments)  # Append to final list

#predicted_departments = get_grievance_department(query_text)
#predicted_outputs.append(predicted_departments)
#print(predicted_output)

accuracy = calculate_accuracy(predicted_outputs, expected_outputs)
print(f"Accuracy: {accuracy:.2f}%")  # Expected: 100.00%


