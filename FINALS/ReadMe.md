Domain : Pet Adoption System

INTERVIEW QUESTIONS

1. In the adoption process, how important is the adopter’s budget? What is the usual range or minimum amount required to adopt or purchase a pet?
a) Not very important — adoption should be based on compassion
b) Moderately important — as long as the adopter can provide basic needs
c) Very important — budget determines the adopter’s readiness
d) Critically important — without enough budget, adoption should be denied
Usual range or minimum:
a) Below ₱5,000
b) ₱5,000 – ₱10,000
c) ₱10,001 – ₱20,000
d) Above ₱20,000

2. Do you usually ask if a person has owned a pet before? How does their past experience affect your decision to approve an adoption?
a) Yes — it strongly affects approval, experienced adopters are prioritized
b) Yes — but it only helps us recommend suitable pets
c) No — past experience is not a major factor
d) Sometimes — only for high-maintenance pets like dogs

3. When evaluating potential adopters, do you consider the type of home they live in (apartment, house, yard)? Why is this detail important?
a) Yes — it determines if the environment suits the pet’s needs
b) Yes — but only for large pets
c) No — as long as the adopter is responsible
d) Sometimes — depending on the pet’s behavior or size

4. How do you assess whether the adopter has enough space for the pet? Do you categorize it as small, medium, or large area?
a) Small — limited indoor space, suitable for cats or small pets
b) Medium — small house with enough room for movement
c) Large — spacious house or yard for active pets like dogs

5. What kinds of pets do most people prefer to adopt, and do different animals require different qualifications or environments?
a) Dogs — need more space and time
b) Cats — suitable for small homes or apartments
c) Rabbits — need moderate space and care
d) Others (birds, hamsters, etc.) — minimal space required

6. Do you take into account whether the adopter already has children or other pets at home? How does that affect your matching process?
a) Yes — it’s a major factor; some pets don’t get along with kids or other animals
b) Yes — but only for aggressive or large pets
c) No — we assume the adopter will adjust
d) Sometimes — depends on the pet’s temperament

7. How do you evaluate if an adopter can afford the pet’s monthly needs (food, grooming, medical care)?
a) Ask their estimated monthly budget
b) Review income or employment status
c) Ask lifestyle-related questions (shopping, travel habits, etc.)
d) We don’t formally check — we trust the adopter’s honesty

8. Do you ask how long the pet would be left alone each day? What is the acceptable number of hours before it becomes a concern?
a) 0–4 hours — ideal
b) 5–8 hours — acceptable for independent pets
c) 9–12 hours — only for certain types (e.g., cats)
d) More than 12 hours — not recommended

9. Are there any background or history checks that might automatically disqualify an adopter (e.g., being underage or neglect history)?
a) Underage (below 18 years old)
b) History of animal neglect or abuse
c) Financial instability
d) Lack of permanent residence
e) None of the above


Fact Structures (Knowledge Engineering)
Adopter:
- AdoptionBudget (Numeric)
- HasPetExperience (Boolean)
- HomeType (String: apartment, house, yard)
- AvailableSpace (String: small, medium, large)
- PreferredPetType (String: dog, cat, rabbit)
- HasChildrenOrOtherPets (Boolean)
- MonthlyPetBudget (Numeric)
- AloneHours (Integer: 0-24)
- AdopterHistoryGood (Boolean)
- AdopterAge (Integer)  // New field for age verification
- EmploymentStatus (String: employed, self-employed, unemployed, student)  // New field
- HasStableIncome (Boolean)  // New field



Rules
    
    IF (AdoptionBudget >= 5000) 
    AND (MonthlyPetBudget >= 3000)
    AND (HasStableIncome = TRUE)
    THEN CareBudget = Sufficient
    ELSE CareBudget = Insufficient

    IF (PreferredPetType = "dog") 
    AND ((AvailableSpace = "large" AND HomeType IN ["house", "yard"]) 
        OR (AvailableSpace = "medium" AND HomeType = "house"))
    THEN SpaceMatch = Suitable
    ELSE IF (PreferredPetType = "cat") 
    AND (AvailableSpace IN ["medium", "large"] OR HomeType != "apartment")
    THEN SpaceMatch = Suitable
    ELSE IF (PreferredPetType = "rabbit")
    AND (AvailableSpace != "small")
    THEN SpaceMatch = Suitable
    ELSE SpaceMatch = Unsuitable

    IF (HasPetExperience = TRUE)
    THEN ExperienceMatch = StronglyApproved
    ELSE IF (PreferredPetType = "rabbit" OR PreferredPetType = "cat")
    THEN ExperienceMatch = Neutral
    ELSE ExperienceMatch = NeedsGuidance

    IF (HasChildrenOrOtherPets = TRUE)
    AND (PreferredPetType = "dog" AND AvailableSpace != "large")
    THEN EnvironmentSuitability = NotRecommended
    ELSE IF (HasChildrenOrOtherPets = TRUE)
    AND (PreferredPetType = "cat")
    THEN EnvironmentSuitability = Conditional
    ELSE EnvironmentSuitability = Suitable

    IF (AloneHours > 8 AND PreferredPetType = "dog")
    THEN TimeAlone = Concerning
    ELSE IF (AloneHours > 12)
    THEN TimeAlone = Unacceptable
    ELSE TimeAlone = Acceptable

    IF (AdoptionStatus = Approved)
    AND (CareBudget = Sufficient)
    AND (SpaceMatch = Suitable)
    AND (ExperienceMatch IN [StronglyApproved, Neutral])
    AND (EnvironmentSuitability != NotRecommended)
    AND (TimeAlone != Unacceptable)
    AND (AdopterAge >= 18)
    THEN FinalDecision = "Adoption Approved"
    ELSE IF (TimeAlone = Concerning OR ExperienceMatch = NeedsGuidance)
    AND (OtherConditionsMet = TRUE)
    THEN FinalDecision = "Conditional Approval - Additional Guidance Required"
    ELSE FinalDecision = "Adoption Not Approved"

    IF (AdopterHistoryGood = FALSE)
    OR (AdopterAge < 18)
    OR (CareBudget = Insufficient)
    OR (TimeAlone = Unacceptable)
    THEN FinalDecision = "Adoption Not Approved"