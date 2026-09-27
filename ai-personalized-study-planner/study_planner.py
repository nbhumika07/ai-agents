from datetime import datetime, date, timedelta


# ============================================================
# AI PERSONALIZED STUDY TIMETABLE GENERATOR
# ============================================================


# ------------------------------------------------------------
# 1. INTRODUCTION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("              📚 AI PERSONALIZED STUDY PLANNER")
print("=" * 70)

print("""
This program creates a personalized and feasible study timetable.

It considers:
• Topic difficulty
• Your current preparation level
• Days remaining until the exam
• Hours available each day
• Your most productive study hours
• Study session length
• Break duration

The program will give more time to difficult and weaker topics
and will shift the focus towards practice and revision as the
exam gets closer.
""")


# ------------------------------------------------------------
# 2. GET EXAM DATE
# ------------------------------------------------------------

while True:

    exam_date_input = input(
        "\n📅 Enter your exam date (DD-MM-YYYY): "
    )

    try:

        exam_date = datetime.strptime(
            exam_date_input,
            "%d-%m-%Y"
        ).date()

        if exam_date <= date.today():

            print(
                "❌ The exam date must be in the future."
            )

            continue

        break

    except ValueError:

        print(
            "❌ Invalid date. Please use DD-MM-YYYY."
        )


days_left = (
    exam_date - date.today()
).days


print(
    f"\n⏳ Days remaining until exam: {days_left}"
)


# ------------------------------------------------------------
# 3. GET DAILY STUDY HOURS
# ------------------------------------------------------------

while True:

    try:

        daily_hours = float(
            input(
                "\n⏰ How many hours can you study per day? "
            )
        )

        if daily_hours <= 0:

            print(
                "❌ Enter a number greater than 0."
            )

            continue

        break

    except ValueError:

        print(
            "❌ Please enter a valid number."
        )


# ------------------------------------------------------------
# 4. GET PRODUCTIVE STUDY HOURS
# ------------------------------------------------------------

print(
    "\n🧠 Now tell me your most productive study period."
)

while True:

    start_input = input(
        "Productive hours START (HH:MM): "
    )

    end_input = input(
        "Productive hours END (HH:MM): "
    )

    try:

        productive_start = datetime.strptime(
            start_input,
            "%H:%M"
        ).time()

        productive_end = datetime.strptime(
            end_input,
            "%H:%M"
        ).time()

        if productive_start >= productive_end:

            print(
                "❌ End time must be later than start time."
            )

            continue

        break

    except ValueError:

        print(
            "❌ Please use 24-hour format, for example 18:00."
        )


# ------------------------------------------------------------
# 5. STUDY SESSION SETTINGS
# ------------------------------------------------------------

while True:

    try:

        session_minutes = int(
            input(
                "\n📖 Preferred study session length "
                "(minutes): "
            )
        )

        if session_minutes <= 0:

            print(
                "❌ Enter a number greater than 0."
            )

            continue

        break

    except ValueError:

        print(
            "❌ Enter a valid number."
        )


while True:

    try:

        break_minutes = int(
            input(
                "☕ Break duration between sessions "
                "(minutes): "
            )
        )

        if break_minutes < 0:

            print(
                "❌ Break duration cannot be negative."
            )

            continue

        break

    except ValueError:

        print(
            "❌ Enter a valid number."
        )


# ------------------------------------------------------------
# 6. GET NUMBER OF TOPICS
# ------------------------------------------------------------

while True:

    try:

        number_topics = int(
            input(
                "\n📚 How many topics do you need to study? "
            )
        )

        if number_topics <= 0:

            print(
                "❌ Enter at least one topic."
            )

            continue

        break

    except ValueError:

        print(
            "❌ Enter a valid number."
        )


# ------------------------------------------------------------
# 7. GET TOPIC INFORMATION
# ------------------------------------------------------------

topics = []

print(
    "\nEnter information about each topic."
)


for i in range(number_topics):

    print(
        f"\n{'-' * 50}"
    )

    print(
        f"TOPIC {i + 1}"
    )

    print(
        f"{'-' * 50}"
    )


    # Topic name

    while True:

        topic_name = input(
            "📚 Topic name: "
        ).strip()

        if topic_name:

            break

        print(
            "❌ Topic name cannot be empty."
        )


    # Difficulty

    while True:

        difficulty = input(
            "📊 Difficulty (Easy / Medium / Hard): "
        ).strip().capitalize()

        if difficulty in [
            "Easy",
            "Medium",
            "Hard"
        ]:

            break

        print(
            "❌ Please enter Easy, Medium or Hard."
        )


    # Preparation

    while True:

        try:

            preparation = int(
                input(
                    "🎯 Current preparation "
                    "(0-100%): "
                )
            )

            if 0 <= preparation <= 100:

                break

            print(
                "❌ Enter a value between 0 and 100."
            )

        except ValueError:

            print(
                "❌ Enter a valid number."
            )


    topics.append({

        "name": topic_name,

        "difficulty": difficulty,

        "preparation": preparation

    })


# ------------------------------------------------------------
# 8. CALCULATE TOPIC PRIORITY
# ------------------------------------------------------------

difficulty_score = {

    "Easy": 1,

    "Medium": 2,

    "Hard": 3

}


for topic in topics:

    difficulty_points = difficulty_score[
        topic["difficulty"]
    ]

    # Low preparation means the topic is weaker.
    weakness = 100 - topic["preparation"]


    # Priority calculation
    #
    # Difficulty = 40% influence
    # Weakness   = 60% influence
    #
    # Higher score = more attention required.

    topic["priority"] = (

        difficulty_points * 40

        + weakness * 0.6

    )


# ------------------------------------------------------------
# 9. SORT TOPICS BY PRIORITY
# ------------------------------------------------------------

topics.sort(

    key=lambda topic: topic["priority"],

    reverse=True

)


# ------------------------------------------------------------
# 10. DISPLAY PRIORITY
# ------------------------------------------------------------

print(
    "\n\n" + "=" * 70
)

print(
    "                  🎯 TOPIC PRIORITY"
)

print(
    "=" * 70
)


for number, topic in enumerate(
    topics,
    start=1
):

    print(

        f"{number}. "
        f"{topic['name']} | "
        f"Difficulty: {topic['difficulty']} | "
        f"Preparation: {topic['preparation']}% | "
        f"Priority: {topic['priority']:.1f}"

    )


# ------------------------------------------------------------
# 11. CALCULATE TOTAL STUDY TIME
# ------------------------------------------------------------

total_available_minutes = (

    days_left

    * daily_hours

    * 60

)


total_priority = sum(

    topic["priority"]

    for topic in topics

)


# ------------------------------------------------------------
# 12. ALLOCATE STUDY TIME TO TOPICS
# ------------------------------------------------------------

for topic in topics:

    topic["allocated_minutes"] = (

        topic["priority"]

        / total_priority

        * total_available_minutes

    )


# ------------------------------------------------------------
# 13. CALCULATE SESSIONS PER DAY
# ------------------------------------------------------------

minutes_available_per_day = (

    daily_hours * 60

)


session_block = (

    session_minutes

    + break_minutes

)


sessions_per_day = int(

    minutes_available_per_day

    // session_block

)


if sessions_per_day <= 0:

    print(
        "\n❌ Your session + break duration is too long "
        "for the available daily study time."
    )

    print(
        "Please restart with shorter sessions or "
        "more daily study hours."
    )

    exit()


# ------------------------------------------------------------
# 14. CALCULATE ACTUAL STUDY TIME
# ------------------------------------------------------------

actual_daily_study_minutes = (

    sessions_per_day

    * session_minutes

)


actual_total_study_minutes = (

    actual_daily_study_minutes

    * days_left

)


# ------------------------------------------------------------
# 15. CREATE REMAINING MINUTES
# ------------------------------------------------------------

remaining_minutes = {

    topic["name"]:
        topic["allocated_minutes"]

    for topic in topics

}


# ------------------------------------------------------------
# 16. GENERATE TIMETABLE
# ------------------------------------------------------------

timetable = []


for day_number in range(
    1,
    days_left + 1
):

    current_date = (

        date.today()

        + timedelta(days=day_number)

    )


    days_until_exam = (

        exam_date

        - current_date

    ).days


    # --------------------------------------------------------
    # STUDY PHASE
    # --------------------------------------------------------

    if days_until_exam <= 2:

        phase = "FINAL REVISION"

    elif days_until_exam <= 5:

        phase = "PRACTICE"

    else:

        phase = "LEARNING"


    # --------------------------------------------------------
    # CREATE DAY'S START TIME
    # --------------------------------------------------------

    current_time = datetime.combine(

        current_date,

        productive_start

    )


    # --------------------------------------------------------
    # CREATE SESSIONS
    # --------------------------------------------------------

    for session_number in range(
        sessions_per_day
    ):


        # Find topics which still need study time

        available_topics = [

            topic

            for topic in topics

            if remaining_minutes[
                topic["name"]
            ] > 0

        ]


        if not available_topics:

            break


        # ----------------------------------------------------
        # CHOOSE TOPIC
        # ----------------------------------------------------

        if phase == "FINAL REVISION":

            # Rotate topics during final revision.

            selected_topic = topics[
                (
                    day_number
                    + session_number
                )
                % len(topics)
            ]

        else:

            # Highest-priority topic gets preference.

            selected_topic = max(

                available_topics,

                key=lambda topic:
                    remaining_minutes[
                        topic["name"]
                    ]

            )


        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        session_start = current_time

        session_end = (

            current_time

            + timedelta(
                minutes=session_minutes
            )

        )


        # ----------------------------------------------------
        # ACTIVITY
        # ----------------------------------------------------

        if phase == "LEARNING":

            if selected_topic[
                "difficulty"
            ] == "Hard":

                activity = (
                    "Deep concept learning + notes"
                )

            elif selected_topic[
                "difficulty"
            ] == "Medium":

                activity = (
                    "Concept learning + examples"
                )

            else:

                activity = (
                    "Learning + short revision"
                )


        elif phase == "PRACTICE":

            activity = (
                "Practice questions + active recall"
            )


        else:

            activity = (
                "Revision + self-testing"
            )


        # ----------------------------------------------------
        # SAVE SESSION
        # ----------------------------------------------------

        timetable.append({

            "day": day_number,

            "date": current_date,

            "start": session_start,

            "end": session_end,

            "topic": selected_topic[
                "name"
            ],

            "difficulty": selected_topic[
                "difficulty"
            ],

            "activity": activity,

            "phase": phase

        })


        # ----------------------------------------------------
        # REDUCE REMAINING TOPIC TIME
        # ----------------------------------------------------

        remaining_minutes[
            selected_topic["name"]
        ] -= session_minutes


        # ----------------------------------------------------
        # NEXT SESSION
        # ----------------------------------------------------

        current_time = (

            session_end

            + timedelta(
                minutes=break_minutes
            )

        )


# ------------------------------------------------------------
# 17. PRINT FINAL TIMETABLE
# ------------------------------------------------------------

print(
    "\n\n" + "=" * 70
)

print(
    "                    📚 YOUR TIMETABLE"
)

print(
    "=" * 70
)


current_day = None


for session in timetable:

    if session["day"] != current_day:

        current_day = session["day"]


        print(
            "\n" + "-" * 70
        )


        print(

            f"📅 DAY {session['day']}  |  "
            f"{session['date'].strftime('%d %B %Y')}"

        )


        print(

            f"📌 STUDY PHASE: "
            f"{session['phase']}"

        )


        print(
            "-" * 70
        )


    print(

        f"\n🕐 "
        f"{session['start'].strftime('%I:%M %p')}"
        f" - "
        f"{session['end'].strftime('%I:%M %p')}"

    )


    print(

        f"📚 Topic: "
        f"{session['topic']}"

    )


    print(

        f"📊 Difficulty: "
        f"{session['difficulty']}"

    )


    print(

        f"🎯 Task: "
        f"{session['activity']}"

    )


    print(

        f"☕ Break afterwards: "
        f"{break_minutes} minutes"

    )


# ------------------------------------------------------------
# 18. SUMMARY
# ------------------------------------------------------------

print(
    "\n\n" + "=" * 70
)

print(
    "                       📊 PLAN SUMMARY"
)

print(
    "=" * 70
)


print(
    f"\n📅 Exam Date: "
    f"{exam_date.strftime('%d %B %Y')}"
)


print(
    f"⏳ Days Remaining: "
    f"{days_left}"
)


print(
    f"⏰ Planned Study Hours/Day: "
    f"{actual_daily_study_minutes / 60:.1f}"
)


print(
    f"📖 Session Length: "
    f"{session_minutes} minutes"
)


print(
    f"☕ Break Length: "
    f"{break_minutes} minutes"
)


print(
    f"🧠 Productive Hours: "
    f"{productive_start.strftime('%I:%M %p')}"
    f" - "
    f"{productive_end.strftime('%I:%M %p')}"
)


print(
    "\n📚 Topic Allocation:"
)


for topic in topics:

    planned_hours = (

        (
            topic["allocated_minutes"]
            / 60
        )

    )


    print(

        f"• {topic['name']}: "
        f"{planned_hours:.1f} hours"

    )


print(
    "\n" + "=" * 70
)

print(
    "           🎉 YOUR STUDY PLAN IS READY!"
)

print(
    "=" * 70
)

print(
    "\nFollow the plan consistently and adjust your "
    "progress as you go. Good luck! 📖"
)