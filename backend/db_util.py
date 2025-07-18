#!/usr/bin/env python3
"""
Database utility script for garden management.
Provides convenient functions to manage the garden database.
"""

import argparse
import json
from database.garden_db import GardenDatabase


def show_stats(db: GardenDatabase):
    """Show database statistics."""
    stats = db.get_database_stats()
    print("🌱 Garden Database Statistics")
    print("=" * 30)
    print(f"Total areals: {stats['total_areals']}")
    print(f"Total plants: {stats['total_plants']}")
    print(f"Healthy plants: {stats['healthy_plants']}")
    print(f"Dead plants: {stats['dead_plants']}")
    print(
        f"Other status: {stats['total_plants'] - stats['healthy_plants'] - stats['dead_plants']}"
    )


def list_areals(db: GardenDatabase):
    """List all areals."""
    areals = db.get_all_areals()
    print("🏡 Garden Areals")
    print("=" * 20)
    for areal in areals:
        print(f"- {areal['name']} ({areal['id']})")
        print(f"  Position: {areal['horizontal_pos']} / {areal['vertical_pos']}")
        print(f"  Size: {areal['size']}")
        plants = db.get_plants_by_areal(areal["id"])
        print(f"  Plants: {len(plants)}")
        print()


def list_plants_by_health(db: GardenDatabase, health: str):
    """List plants by health status."""
    plants = db.get_plants_by_health(health)
    print(f"🌿 Plants with status: {health}")
    print("=" * 30)
    for plant in plants:
        print(f"- {plant['name']} (in {plant['areal_name']})")
        print(f"  Size: {plant['size']}, Position: {plant['position']}")
        print(f"  Image: {plant['image_path']}")
        print()


def export_garden_data(db: GardenDatabase, output_file: str):
    """Export garden data to JSON file."""
    data = db.get_garden_data()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Garden data exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Garden Database Utility")
    parser.add_argument("--db", default="garden.db", help="Database file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")

    # List commands
    subparsers.add_parser("areals", help="List all areals")

    health_parser = subparsers.add_parser("plants", help="List plants by health status")
    health_parser.add_argument(
        "health", choices=["healthy", "okay", "dead"], help="Health status to filter by"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export garden data to JSON")
    export_parser.add_argument("output", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize database
    db = GardenDatabase(args.db)

    # Execute command
    if args.command == "stats":
        show_stats(db)
    elif args.command == "areals":
        list_areals(db)
    elif args.command == "plants":
        list_plants_by_health(db, args.health)
    elif args.command == "export":
        export_garden_data(db, args.output)


if __name__ == "__main__":
    main()
