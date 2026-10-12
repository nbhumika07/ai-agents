# Mini Autonomous Travel Agent

A small Python project for learning how an AI travel agent can search for a trip, compare it with a budget, remember preferences, try a new plan when needed, and wait for approval before a simulated booking.

> **Demo only:** The flights, hotels, and prices are sample data. This program does not search live travel sites, reserve tickets or rooms, or take payments.

## What the program does

1. Collects your route, travel date, number of nights, and budget in Indian rupees (INR).
2. Searches the included sample flight and hotel data.
3. Checks your hotel requirements and whether the total fits your budget.
4. If no hotel meets the first nightly price limit, tries again up to two times, staying within the maximum nightly price you entered.
5. Shows a proposed trip and waits for you to type `approve` or `deny`.
6. Creates a simulated confirmation only after you approve.

## Files

```text
mini-autonomous-travel-agent/
├── stateful_agent/
│   ├── __init__.py
│   ├── __main__.py
│   ├── agent.py          # Agent state machine and approval check
│   ├── cli.py            # Questions and trip summary shown in the terminal
│   ├── llm.py            # Optional OpenAI reflection; local fallback included
│   ├── memory.py         # Short-term and saved preference memory
│   ├── models.py         # Validated data models
│   └── tools.py          # Sample flight, hotel, and booking tools
├── .env.example          # Example settings; contains no real API key
├── .gitignore            # Keeps secrets and generated files out of GitHub
├── README.md
└── requirements.txt
