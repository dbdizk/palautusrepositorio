from rich.console import Console
from rich.table import Table
from player import PlayerReader, PlayerStats


def create_table(players, season: str, nationality: str) -> Table:
    table = Table(title=f"Season {season} players from {nationality}")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Teams")
    table.add_column("Goals")
    table.add_column("Assists")
    table.add_column("Points")

    for player in players:
        table.add_row(*player.to_row())

    return table


def main() -> None:
    season = input("Enter season (format '2020-21'): ")
    nationality = input("Enter nationality (format 'FIN, USA'): ")

    url = f"https://studies.cs.helsinki.fi/nhlstats/{season}/players"
    reader = PlayerReader(url)
    stats = PlayerStats(reader)
    players = stats.top_scorers_by_nationality(nationality)

    table = create_table(players, season, nationality)
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
