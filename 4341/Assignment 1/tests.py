from main import main

for i in range(1,7):
    print(f"Heuristic: {i}")
    main('board.txt', i)
    print("\n\n\n")
