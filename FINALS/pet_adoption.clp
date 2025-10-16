(deftemplate adopter
  (slot AdoptionBudget)     ; Numeric value for initial adoption cost
  (slot HasPetExperience)   ; Boolean: true if has pet experience
  (slot HomeType)           ; apartment, house, or yard
  (slot AvailableSpace)     ; small, medium, or large
  (slot PreferredPetType)   ; dog, cat, or rabbit
  (slot HasChildrenOrOtherPets) ; Boolean
  (slot MonthlyPetBudget)   ; Numeric value for monthly expenses
  (slot AloneHours)         ; Integer: hours pet will be alone daily
  (slot AdopterHistoryGood) ; Boolean: true if no history issues
  )

(deftemplate decision
  (slot AdoptionStatus (default pending))
  (slot CareBudget (default pending))
  (slot SpaceMatch (default pending))
  (slot AdoptionRecommendation (default pending))
  (slot ExperienceMatch (default pending))
  (slot FinalDecision (default pending)))

;; --- Rules with proper salience (priority) ---

;; Phase 1: Check individual criteria (highest priority)
(defrule check-budget
  (declare (salience 100))
  (adopter (AdoptionBudget ?b) (PreferredPetType ?pet))
  ?d <- (decision (CareBudget pending))
  =>
  (bind ?required (if (eq ?pet "dog") then 5000
                    else if (eq ?pet "cat") then 3000
                    else 2000))  ; rabbit
  (if (>= ?b ?required)
      then (modify ?d (CareBudget Sufficient))
      else (modify ?d (CareBudget Insufficient)
                   (FinalDecision (str-cat "Adoption Rejected - Insufficient budget (need at least " ?required ")"))))

(defrule check-space
  (declare (salience 100))
  (adopter (AvailableSpace ?s) (PreferredPetType ?pet) (HomeType ?ht))
  ?d <- (decision (SpaceMatch pending))
  =>
  (bind ?suitable (or (eq ?pet "rabbit")  ; Rabbits need less space
                    (and (or (eq ?s "medium") (eq ?s "large"))
                         (or (eq ?ht "house") (eq ?ht "yard")))))
  (if (eq ?suitable TRUE) then
      (modify ?d (SpaceMatch Suitable))
    else
      (modify ?d (SpaceMatch Unsuitable)
               (FinalDecision "Adoption Rejected - Insufficient space (need house/yard for dogs/cats)")))

(defrule check-experience
  (declare (salience 100))
  (adopter (HasPetExperience ?e) (PreferredPetType ?pet))
  ?d <- (decision (ExperienceMatch pending))
  =>
  (if (and ?e (or (eq ?pet "dog") (eq ?pet "cat")))
      then (modify ?d (ExperienceMatch StronglyApproved))
      else (modify ?d (ExperienceMatch Neutral)
                   (if (and (not ?e) (or (eq ?pet "dog") (eq ?pet "cat")))
                       then (FinalDecision "Adoption Pending - Consider gaining pet experience first")
                       else (FinalDecision pending))))

(defrule check-availability
  (declare (salience 100))
  (adopter (AloneHours ?hours) (AdopterHistoryGood ?history))
  ?d <- (decision (AdoptionStatus pending))
  =>
  (if (not ?history)
      then (modify ?d (AdoptionStatus Rejected)
                   (FinalDecision "Adoption Rejected - History concerns detected"))
      else if (> ?hours 12)
      then (modify ?d (AdoptionStatus Rejected)
                   (FinalDecision "Adoption Rejected - Pet would be alone for too long (max 12 hours)"))
      else (modify ?d (AdoptionStatus Approved))))

;; Phase 2: Make recommendation (medium priority)
(defrule recommendation
  (declare (salience 50))
  (adopter (HasChildrenOrOtherPets ?hasOthers) (PreferredPetType ?pet))
  ?d <- (decision (AdoptionRecommendation pending))
  =>
  (if (and ?hasOthers (or (eq ?pet "dog") (eq ?pet "large dog")))
      then (modify ?d (AdoptionRecommendation NotRecommended)
                   (FinalDecision "Adoption Not Recommended - Large dogs not recommended with children/other pets"))
      else (modify ?d (AdoptionRecommendation Recommended))))

;; Phase 3: Final decision (lowest priority)
(defrule final-approval
  (declare (salience 5))
  ?d <- (decision (AdoptionStatus Approved)
                  (CareBudget Sufficient)
                  (SpaceMatch Suitable)
                  (AdoptionRecommendation Recommended)
                  (FinalDecision pending))
  =>
  (modify ?d (FinalDecision "Adoption Approved - All criteria met!")))

(defrule final-pending-experience
  (declare (salience 5))
  ?d <- (decision (AdoptionStatus Approved)
                  (CareBudget Sufficient)
                  (SpaceMatch Suitable)
                  (ExperienceMatch Neutral)
                  (AdoptionRecommendation Recommended)
                  (FinalDecision pending))
  =>
  (modify ?d (FinalDecision "Adoption Conditionally Approved - Consider gaining pet experience first")))

(defrule final-reject-children-large-dog
  (declare (salience 5))
  ?d <- (decision (AdoptionRecommendation NotRecommended)
                  (FinalDecision pending))
  =>
  (modify ?d (FinalDecision "Adoption Not Recommended - Large dogs not suitable with children/other pets")))

(defrule final-reject-budget
  (declare (salience 5))
  ?d <- (decision (CareBudget Insufficient)
                  (FinalDecision pending))
  =>
  (modify ?d (FinalDecision "Adoption Rejected - Insufficient budget for pet type")))

(defrule final-reject-space
  (declare (salience 5))
  ?d <- (decision (SpaceMatch Unsuitable)
                  (FinalDecision pending))
  =>
  (modify ?d (FinalDecision "Adoption Rejected - Insufficient space for pet type")))

(defrule final-reject-multiple
  (declare (salience 5))
  ?d <- (decision (CareBudget Insufficient)
                  (SpaceMatch Unsuitable)
                  (FinalDecision pending))
  =>
  (modify ?d (FinalDecision "Adoption Rejected - Multiple criteria not met (budget and space)")))