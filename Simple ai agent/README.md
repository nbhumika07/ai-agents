
# AI Study Planner

A simple Python-based study planner that generates a day-wise study timetable based on the subject you choose and the number of days remaining until your exam.

The planner distributes topics across available study days, schedules revision sessions, and reserves the final day for overall revision and practice questions.

## Features

- **Predefined Subjects:** Choose from DBMS, DSA, or Java, each with a predefined list of topics.
- **Automatic Timetable Generation:** Distributes topics across the available study days.
- **Revision Scheduling:** Includes revision sessions every second day to reinforce previously studied topics.
- **Dedicated Revision Day:** Reserves the last day for full revision and practice questions.
- **Input Validation:** Handles invalid subjects, non-numeric inputs, and non-positive day counts.
- **Command-Line Interface:** Interact with the planner directly through the terminal.

## Technologies Used

- **Language:** Python 3
- **Concepts:** Dictionaries, lists, functions, loops, conditional statements, user input, and exception handling.

## Available Subjects

| Subject | Topics Covered |
|---|---|
| DBMS | Introduction to DBMS, ER Model, Relational Model, SQL, Normalization, Transactions, Indexing |
| DSA | Arrays, Strings, Linked Lists, Stacks, Queues, Trees, Graphs |
| Java | OOP Concepts, Classes and Objects, Inheritance, Polymorphism, Exception Handling, Collections, Multithreading |

## How It Works

1. Select a subject: Enter DBMS, DSA, or Java.
2. Enter the number of days remaining until your exam.
3. Generate the timetable: The program distributes topics across the available study days.
4. Revise previous topics: Revision sessions are added every second day when previously scheduled topics are available.
5. Prepare for the exam: The final day is reserved for full revision and practice questions or a mock test.

The scheduling logic uses integer division and the remainder operator to distribute topics as evenly as possible across the study days.

## Getting Started

### Prerequisites

- Python 3 installed on your system.
- A terminal or command prompt.

No external libraries are required.

### Installation and Execution

**1. Clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/ai-study-planner.git
```

Replace `YOUR-USERNAME` with your GitHub username and use your actual repository name.

**2. Navigate to the project directory**

```bash
cd ai-study-planner
```

**3. Run the program**

```bash
python main.py
```

If your system uses the `python3` command, run:

```bash
python3 main.py
```

Make sure your Python file is named `main.py`, or replace it with your actual filename.

## Example Usage

```text
========================================
        AI STUDY PLANNER
========================================

Enter the subject: DBMS
Enter number of days until exam: 4

========================================
        YOUR STUDY TIMETABLE
========================================

Subject: DBMS
Days: 4

--- DAY 1 ---
• Study: Introduction to DBMS
• Study: ER Model

--- DAY 2 ---
• Study: Relational Model
• Study: SQL
• Revision: Introduction to DBMS, ER Model

--- DAY 3 ---
• Study: Normalization
• Study: Transactions

--- DAY 4 ---
• Full Revision - All Topics
• Practice Questions / Mock Test
```

*Note: This example illustrates the output format. The actual topic distribution depends on the number of days entered.*

## Project Structure

```text
ai-study-planner/
│
├── simpleai.py        # Main program and timetable generation logic
└── README.md      # Project documentation
```

## Future Improvements

- Allow users to add custom subjects and topics.
- Consider topic difficulty and priority when generating schedules.
- Include daily study-hour preferences and time slots.
- Track completed topics and pending revision sessions.
- Add a graphical user interface or web-based dashboard.
- Integrate AI to generate personalized study plans based on learning goals and deadlines.

## Project Objective

The goal of this project is to simplify exam preparation by organizing topics into a structured study schedule and encouraging regular revision.

---

**Built with Python | Designed to make exam preparation more organized.**

