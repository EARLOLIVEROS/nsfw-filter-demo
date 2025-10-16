import tkinter as tk
from tkinter import messagebox, scrolledtext
import clips

# ============== CLIPS EXECUTION ==============
def run_clips(adopter_data):
    env = clips.Environment()
    env.load("pet_adoption.clp")
    env.reset()

    # CRITICAL: Don't use quotes for boolean/symbol values in CLIPS
    fact_str = f"""
    (adopter
        (AdoptionBudget {adopter_data['budget']})
        (HasPetExperience {adopter_data['experience']})
        (HomeType {adopter_data['home']})
        (AvailableSpace {adopter_data['space']})
        (PreferredPetType "{adopter_data['pet']}")
        (HasChildrenOrOtherPets {adopter_data['children']})
        (MonthlyPetBudget {adopter_data['monthly']})
        (AloneHours {adopter_data['hours']})
        (AdopterHistoryGood {adopter_data['record']})
    )
    """
    
    print("DEBUG: Asserting fact:")
    print(fact_str)

    env.assert_string(fact_str)
    env.assert_string("(decision)")
    env.run()

    # Get the decision fact
    decision_fact = None
    for fact in env.facts():
        if "decision" in str(fact):
            decision_fact = fact
            break
    
    if decision_fact:
        # Extract values from the decision fact
        result = {
            'AdoptionStatus': decision_fact['AdoptionStatus'],
            'CareBudget': decision_fact['CareBudget'],
            'SpaceMatch': decision_fact['SpaceMatch'],
            'ExperienceMatch': decision_fact['ExperienceMatch'],
            'AdoptionRecommendation': decision_fact['AdoptionRecommendation'],
            'FinalDecision': decision_fact['FinalDecision']
        }
        return result
    else:
        return {'error': 'No decision generated'}


# ============== GUI APP ==============
class PetAdoptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🐾 Pet Adoption Expert System")
        self.root.geometry("650x500")
        self.root.configure(bg="#f0f0f0")

        self.questions = [
            {
                "text": "1. In the adoption process, how important is the adopter's budget?",
                "type": "choice",
                "options": [
                    "Not very important — adoption should be based on compassion",
                    "Moderately important — as long as the adopter can provide basic needs",
                    "Very important — budget determines the adopter's readiness",
                    "Critically important — without enough budget, adoption should be denied"
                ],
                "key": "budget_importance"
            },
            {
                "text": "2. What is the usual range or minimum amount required to adopt or purchase a pet?",
                "type": "choice",
                "options": [
                    "Below ₱5,000",
                    "₱5,000 – ₱10,000",
                    "₱10,001 – ₱20,000",
                    "Above ₱20,000"
                ],
                "key": "budget_range"
            },
            {
                "text": "3. Do you usually ask if a person has owned a pet before? How does their past experience affect your decision to approve an adoption?",
                "type": "choice",
                "options": [
                    "Yes — it strongly affects approval, experienced adopters are prioritized",
                    "Yes — but it only helps us recommend suitable pets",
                    "No — past experience is not a major factor",
                    "Sometimes — only for high-maintenance pets like dogs"
                ],
                "key": "experience"
            },
            {
                "text": "4. When evaluating potential adopters, do you consider the type of home they live in (apartment, house, yard)? Why is this detail important?",
                "type": "choice",
                "options": [
                    "Yes — it determines if the environment suits the pet's needs",
                    "Yes — but only for large pets",
                    "No — as long as the adopter is responsible",
                    "Sometimes — depending on the pet's behavior or size"
                ],
                "key": "home_type"
            },
            {
                "text": "5. How do you assess whether the adopter has enough space for the pet? Do you categorize it as small, medium, or large area?",
                "type": "choice",
                "options": [
                    "Small — limited indoor space, suitable for cats or small pets",
                    "Medium — small house with enough room for movement",
                    "Large — spacious house or yard for active pets like dogs"
                ],
                "key": "available_space"
            },
            {
                "text": "6. What kinds of pets do most people prefer to adopt, and do different animals require different qualifications or environments?",
                "type": "choice",
                "options": [
                    "Dogs — need more space and time",
                    "Cats — suitable for small homes or apartments",
                    "Rabbits — need moderate space and care",
                    "Others (birds, hamsters, etc.) — minimal space required"
                ],
                "key": "pet_type"
            },
            {
                "text": "7. Do you take into account whether the adopter already has children or other pets at home? How does that affect your matching process?",
                "type": "choice",
                "options": [
                    "Yes — it's a major factor; some pets don't get along with kids or other animals",
                    "Yes — but only for aggressive or large pets",
                    "No — we assume the adopter will adjust",
                    "Sometimes — depends on the pet's temperament"
                ],
                "key": "children_pets"
            },
            {
                "text": "8. How do you evaluate if an adopter can afford the pet's monthly needs (food, grooming, medical care)?",
                "type": "choice",
                "options": [
                    "Ask their estimated monthly budget",
                    "Review income or employment status",
                    "Ask lifestyle-related questions (shopping, travel habits, etc.)",
                    "We don't formally check — we trust the adopter's honesty"
                ],
                "key": "affordability"
            },
            {
                "text": "9. Do you ask how long the pet would be left alone each day? What is the acceptable number of hours before it becomes a concern?",
                "type": "choice",
                "options": [
                    "0–4 hours — ideal",
                    "5–8 hours — acceptable for independent pets",
                    "9–12 hours — only for certain types (e.g., cats)",
                    "More than 12 hours — not recommended"
                ],
                "key": "alone_hours"
            },
            {
                "text": "10. Are there any background or history checks that might automatically disqualify an adopter?",
                "type": "choice",
                "options": [
                    "Underage (below 18 years old)",
                    "History of animal neglect or abuse",
                    "Financial instability",
                    "Lack of permanent residence",
                    "None of the above"
                ],
                "key": "disqualifiers"
            }
        ]

        self.answers = {}
        self.current_question = 0

        # Title
        title_label = tk.Label(root, text="🐾 Pet Adoption Expert System", 
                              font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title_label.pack(pady=20)

        # Question label
        self.label = tk.Label(root, text="", wraplength=550, font=("Arial", 13), 
                             bg="#f0f0f0", fg="#34495e", justify="left")
        self.label.pack(pady=20)

        # Input frame
        self.frame = tk.Frame(root, bg="#f0f0f0")
        self.frame.pack(pady=20)

        self.entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.var_choice = tk.StringVar()
        self.var_bool = tk.IntVar()

        # Button frame
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(pady=30)

        self.back_button = tk.Button(button_frame, text="⬅️ Back", command=self.prev_question, 
                                     bg="#95a5a6", fg="white", width=12, font=("Arial", 11))
        self.back_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(button_frame, text="Next ➡️", command=self.next_question, 
                                     bg="#27ae60", fg="white", width=12, font=("Arial", 11, "bold"))
        self.next_button.pack(side=tk.LEFT, padx=10)

        # Progress label
        self.progress_label = tk.Label(root, text="", font=("Arial", 10), 
                                       bg="#f0f0f0", fg="#7f8c8d")
        self.progress_label.pack(pady=5)

        self.show_question()

    def show_question(self):
        q = self.questions[self.current_question]
        self.label.config(text=q["text"])
        
        # Clear previous widgets
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.entry.pack_forget()

        # Update progress
        self.progress_label.config(text=f"Question {self.current_question + 1} of {len(self.questions)}")
        
        # Show/hide back button
        if self.current_question == 0:
            self.back_button.config(state=tk.DISABLED)
        else:
            self.back_button.config(state=tk.NORMAL)

        # Update next button text
        if self.current_question == len(self.questions) - 1:
            self.next_button.config(text="Submit ✅")
        else:
            self.next_button.config(text="Next ➡️")

        # Show appropriate input widget
        if q["type"] == "int":
            self.entry.delete(0, tk.END)
            if q["key"] in self.answers:
                self.entry.insert(0, str(self.answers[q["key"]]))
            self.entry.pack()
            self.entry.focus()
        elif q["type"] == "bool":
            current_val = self.answers.get(q["key"], "true")
            self.var_bool.set(1 if current_val == "true" else 0)
            tk.Radiobutton(self.frame, text="✓ Yes", variable=self.var_bool, value=1, 
                          font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
            tk.Radiobutton(self.frame, text="✗ No", variable=self.var_bool, value=0, 
                          font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        elif q["type"] == "choice":
            current_val = self.answers.get(q["key"], q["options"][0])
            self.var_choice.set(current_val)
            for option in q["options"]:
                tk.Radiobutton(self.frame, text=option.capitalize(), variable=self.var_choice, 
                              value=option, font=("Arial", 12), bg="#f0f0f0").pack(pady=5)

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def next_question(self):
        q = self.questions[self.current_question]
        try:
            if q["type"] == "int":
                value = int(self.entry.get())
                if value < 0:
                    messagebox.showerror("Error", "Please enter a positive number.")
                    return
            elif q["type"] == "bool":
                value = "true" if self.var_bool.get() == 1 else "false"
            elif q["type"] == "choice":
                value = self.var_choice.get()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        self.answers[q["key"]] = value

        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.evaluate()

    def evaluate(self):
        # Create a new window for results
        result_window = tk.Toplevel(self.root)
        result_window.title("Adoption Evaluation Results")
        result_window.geometry("600x500")
        result_window.configure(bg="#ecf0f1")
        
        # Title
        title = tk.Label(result_window, text="Adoption Evaluation Summary", 
                        font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title.pack(pady=10)
        
        # Create a frame for the results
        result_frame = tk.Frame(result_window, bg="white", padx=20, pady=15)
        result_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Map question keys to display labels
        field_labels = {
            'budget_importance': "Adopter's budget:",
            'budget_range': "Amount range:",
            'experience': "Experience:",
            'home_type': "Home type:",
            'available_space': "Space:",
            'pet_type': "People prefer:",
            'children_pets': "Has children or other pets:",
            'affordability': "Evaluating monthly needs:",
            'alone_hours': "Hours left at home:",
            'disqualifiers': "Automatically disqualify for adopting:"
        }
        
        # Display each answer in the specified format
        row = 0
        for key, label in field_labels.items():
            # Get the selected answer, or "Not answered" if not found
            answer = self.answers.get(key, "Not answered")
            
            # Create label
            lbl = tk.Label(result_frame, text=label, font=("Arial", 10, "bold"), 
                          bg="white", fg="#2c3e50", anchor="w", width=30)
            lbl.grid(row=row, column=0, sticky="w", pady=2)
            
            # Create answer display
            ans = tk.Label(result_frame, text=f'"{answer}"', font=("Arial", 10), 
                          bg="white", fg="#3498db", anchor="w")
            ans.grid(row=row, column=1, sticky="w", pady=2)
            
            row += 1
        
        # Add a separator
        separator = tk.Frame(result_window, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Close button
        close_btn = tk.Button(result_window, text="Close", 
                             command=result_window.destroy,
                             bg="#3498db", fg="white", 
                             width=15, font=("Arial", 11, "bold"))
        close_btn.pack(pady=10)


# ============== RUN APP ==============
if __name__ == "__main__":
    root = tk.Tk()
    app = PetAdoptionApp(root)
    root.mainloop()