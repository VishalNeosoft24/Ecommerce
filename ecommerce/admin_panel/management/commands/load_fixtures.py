from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = "Load data from multiple fixtures into the database"

    def handle(self, *args, **kwargs):
        # Define the path to the fixtures directory
        fixtures_dir = os.path.join("admin_panel", "fixtures")

        # List of fixture files to load (without .json)
        fixture_files = [
            "initial_groups_data",
            "initial_user_data",
            "initial_emailtemplate_data",
            "initial_banner_data",
            "initial_flatpages_data",
            "initial_categories_data",
            "initial_address_data",
        ]

        for fixture in fixture_files:
            fixture_path = os.path.join(fixtures_dir, f"{fixture}.json")
            try:
                self.stdout.write(f"Loading fixture: {fixture_path}")
                call_command("loaddata", fixture_path)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error loading fixture {fixture_path}: {e}")
                )

        self.stdout.write(self.style.SUCCESS("Successfully loaded all fixtures."))
