import requests
import random
import time
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

def get_random_sentence():
    url = "https://uk.wikipedia.org/api/rest_v1/page/random/summary"
    response = requests.get(url).json()
    sentence = response["extract"].split(". ")[0]
    words = sentence.split()
    if len(words) < 5:
        return get_random_sentence()
    return sentence

def shuffle_sentence(sentence):
    words = sentence.split()
    random.shuffle(words)
    return " ".join(words), words

def load_leaderboard():
    try:
        with open("leaderboard.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_leaderboard(name, score, accuracy):
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "score": score, "accuracy": accuracy})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    with open("leaderboard.json", "w") as file:
        json.dump(leaderboard[:10], file, indent=4)

def show_leaderboard(console):
    leaderboard = load_leaderboard()
    table = Table(title="Таблиця лідерів")
    table.add_column("Місце", justify="center")
    table.add_column("Ім'я", justify="center")
    table.add_column("Очки", justify="center")
    table.add_column("Точність", justify="center")
    
    for i, entry in enumerate(leaderboard, 1):
        table.add_row(str(i), entry["name"], str(entry["score"]), f"{entry['accuracy']}%")
    
    console.print(table)

def play_game():
    console = Console()
    score = 0
    lives = 3
    correct_answers = 0
    total_time = 0
    rounds = 5
    
    console.print("[bold cyan]Вітаємо в грі 'Віднови речення'![/bold cyan]")
    name = Prompt.ask("Введіть своє ім'я")
    difficulty = Prompt.ask("Оберіть рівень складності", choices=["легкий", "середній", "складний"], default="середній")
    time_limit = {"легкий": 30, "середній": 20, "складний": 10}[difficulty]
    point_multiplier = {"легкий": 1, "середній": 2, "складний": 3}[difficulty]
    
    for round_num in range(1, rounds + 1):
        console.print(f"[bold yellow]Раунд {round_num}[/bold yellow]")
        sentence = get_random_sentence()
        shuffled, words = shuffle_sentence(sentence)
        
        console.print(f"[bold yellow]Розставте слова у правильному порядку:[/bold yellow] {shuffled}")
        
        start_time = time.time()
        user_input = input("Ваш варіант: ")
        elapsed_time = time.time() - start_time
        total_time += elapsed_time
        
        if elapsed_time > time_limit:
            console.print("[red]Час вийшов! Ви втратили життя.[/red]")
            lives -= 1
        elif user_input.strip() == sentence.strip():
            console.print("[green]Правильно![/green]")
            score += 10 * point_multiplier
            correct_answers += 1
        else:
            console.print(f"[red]Неправильно![/red] Правильне речення: {sentence}")
            lives -= 1
        
        if lives == 0:
            console.print("[bold red]Гра завершена! Ви втратили всі життя.[/bold red]")
            break
    
    accuracy = round((correct_answers / rounds) * 100, 2)
    avg_time = round(total_time / rounds, 2)
    
    console.print(f"[bold cyan]Гра завершена! Ваш рахунок: {score}[/bold cyan]")
    console.print(f"[bold cyan]Точність: {accuracy}%, середній час відповіді: {avg_time} секунд[/bold cyan]")
    save_leaderboard(name, score, accuracy)
    show_leaderboard(console)
    
if __name__ == "__main__":
    play_game()