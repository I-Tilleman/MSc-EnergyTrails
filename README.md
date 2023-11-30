# EnergyTrails
Repository for the implementation of the simulation the Energy Trails game, which is part of the Master Thesis called "Smart Negotiators for a Smarter Grid: Exploring the Potential of Theory of Mind in Energy Regulation" by Isabelle Tilleman. This Master's Thesis was supervised by prof. dr. Rineke Verbrugge (Artificial Intelligence, University of Groningen)
    and
    dr. Wico Mulder (TNO, Groningen). 

Original code, which this code was based on, was written by [Harmen de Weerd](https://www.harmendeweerd.nl/). 

## How to run

### General set-up 
- Make sure Poetry and Python are installed. 
- Install the project dependencies by running ```poetry install``` inside the repository

### Running a single negotiation
- Adjust the ```test.py``` file on line 17 to run a negotiation with the orders of theory of mind that you want to test
- Run the negotiation with ```poetry run python3 EnergyTrails/test.py```

### Running multiple negotiations 
- Run multiple negotiations with ```poetry run python3 EnergyTrails/multiple_negotiations.py <agents> <backup-frequency> <number of negotiations> <negotiation round limit> <number of boards> <point sharing TRUE/FALSE>``` 

**EXAMPLE:**
If you want to run 100 negotiations with a ToM1 and ToM2 agent pairing, with a negotiation round limit of 25, 4 boards, and point sharing (cooperative scoring), which backs up the results every 10 negotiations, run:  
```poetry run python3 EnergyTrails/multiple_negotiations.py 12 10 100 25 4 1```

