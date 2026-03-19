import json
from app.supervisor.supervisor import LoanSupervisor

def main():
    with open("data/applications/app_001.json") as f:
        app = json.load(f)

    supervisor = LoanSupervisor()
    state = supervisor.run(app)

    print("\n===== FINAL STATE =====\n")
    print(json.dumps(state.to_dict(), indent=2))

if __name__ == "__main__":
    main()