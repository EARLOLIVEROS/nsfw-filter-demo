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
                "text": "1. How important is your budget for adopting a pet?",
                "type": "choice",
                "options": [
                    "Not very important - adoption should be based on compassion",
                    "Moderately important - as long as I can provide basic needs",
                    "Very important - budget determines my readiness",
                    "Critically important - I need to stay within my budget"
                ],
                "key": "budget_importance"
            },
            {
                "text": "2. What is your adoption budget range? (in pesos)",
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
                "text": "3. Have you ever owned a pet before? How does this affect your adoption?",
                "type": "choice",
                "options": [
                    "Yes - I have experience and should be prioritized",
                    "Yes - it helps me choose suitable pets",
                    "No - past experience is not a major factor",
                    "Sometimes - only for certain pets"
                ],
                "key": "experience"
            },
            {
                "text": "4. What type of home do you live in?",
                "type": "choice",
                "options": ["Apartment", "House", "Yard"],
                "key": "home_type"
            },
            {
                "text": "5. How much space do you have available for a pet?",
                "type": "choice",
                "options": ["Small", "Medium", "Large"],
                "key": "available_space"
            },
            {
                "text": "6. What type of pet are you most interested in adopting?",
                "type": "choice",
                "options": ["Dog", "Cat", "Rabbit"],
                "key": "pet_type"
            },
            {
                "text": "7. Do you have children or other pets at home?",
                "type": "choice",
                "options": [
                    "Yes - it's a major factor in pet selection",
                    "Yes - but only for certain pets",
                    "No - I can adjust to any pet's needs",
                    "Sometimes - depends on the pet's temperament"
                ],
                "key": "children_pets"
            },
            {
                "text": "8. How do you plan to afford the pet's monthly needs?",
                "type": "choice",
                "options": [
                    "I have a specific monthly budget set aside",
                    "My income can support regular expenses",
                    "I'm still evaluating the costs",
                    "I prefer not to say"
                ],
                "key": "affordability"
            },
            {
                "text": "9. How many hours will the pet be alone each day?",
                "type": "choice",
                "options": [
                    "0-4 hours - I work from home or am mostly at home",
                    "5-8 hours - typical workday hours",
                    "9-12 hours - long workdays",
                    "More than 12 hours - I'm often away"
                ],
                "key": "alone_hours"
            },
            {
                "text": "10. Do any of these apply to your situation?",
                "type": "choice",
                "options": [
                    "I am under 18 years old",
                    "I have a history of animal neglect or abuse",
                    "I have financial instability",
                    "I don't have a permanent residence",
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
        result = run_clips(self.answers)
        
        if 'error' in result:
            messagebox.showerror("Error", result['error'])
            return
        
        # Create result window
        result_window = tk.Toplevel(self.root)
        result_window.title("🐾 Adoption Evaluation Result")
        result_window.geometry("600x450")
        result_window.configure(bg="#ecf0f1")
        
        # Title
        title = tk.Label(result_window, text="Pet Adoption Evaluation Result", 
                        font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title.pack(pady=20)
        
        # Result text area
        text_area = scrolledtext.ScrolledText(result_window, width=65, height=15, 
                                              font=("Courier", 10), bg="white", 
                                              fg="#2c3e50", wrap=tk.WORD)
        text_area.pack(pady=10, padx=20)
        
        # Format results
        result_text = "="*60 + "\n"
        result_text += "ADOPTION EVALUATION SUMMARY\n"
        result_text += "="*60 + "\n\n"
        
        result_text += f"📋 Adoption Status:      {result['AdoptionStatus']}\n"
        result_text += f"💰 Care Budget:          {result['CareBudget']}\n"
        result_text += f"🏠 Space Match:          {result['SpaceMatch']}\n"
        result_text += f"🎓 Experience Match:     {result['ExperienceMatch']}\n"
        result_text += f"💡 Recommendation:       {result['AdoptionRecommendation']}\n"
        result_text += "\n" + "-"*60 + "\n"
        
        final_decision = result['FinalDecision']
        if "Approved" in final_decision:
            result_text += f"✅ FINAL DECISION:\n   {final_decision}\n"
        else:
            result_text += f"❌ FINAL DECISION:\n   {final_decision}\n"
        
        result_text += "-"*60 + "\n\n"
        
        # Add user inputs
        result_text += "Your Inputs:\n"
        result_text += f"  • Budget: ₱{self.answers['budget']}\n"
        result_text += f"  • Monthly Budget: ₱{self.answers['monthly']}\n"
        result_text += f"  • Experience: {self.answers['experience']}\n"
        result_text += f"  • Home Type: {self.answers['home']}\n"
        result_text += f"  • Space: {self.answers['space']}\n"
        result_text += f"  • Preferred Pet: {self.answers['pet']}\n"
        result_text += f"  • Has Children/Pets: {self.answers['children']}\n"
        result_text += f"  • Pet Alone Hours: {self.answers['hours']}\n"
        result_text += f"  • Good History: {self.answers['record']}\n"
        
        text_area.insert(tk.END, result_text)
        text_area.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(result_window, text="Close", command=lambda: [result_window.destroy(), self.root.destroy()],
                             bg="#e74c3c", fg="white", width=15, font=("Arial", 11, "bold"))
        close_btn.pack(pady=15)


# ============== RUN APP ==============
if __name__ == "__main__":
    root = tk.Tk()
    app = PetAdoptionApp(root)
    root.mainloop()