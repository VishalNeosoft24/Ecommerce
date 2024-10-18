# admin_panel/management/commands/start_all_servers.py

from django.core.management.commands.runserver import Command as RunserverCommand
import subprocess
import time
import atexit


# class Command(RunserverCommand):
#     help = "Start all extra servers: Redis, Celery worker, Celery Beat, and ngrok"

#     def handle(self, *args, **options):
#         # Start Redis server
#         redis_process = subprocess.Popen(
#             ["redis-server"],
#         )
#         print("Redis server started.")

#         # Start Celery worker
#         celery_worker_process = subprocess.Popen(
#             ["celery", "-A", "ecommerce", "worker", "--loglevel=info"]
#         )
#         print("Celery worker started.")

#         # Start Celery Beat
#         celery_beat_process = subprocess.Popen(
#             ["celery", "-A", "ecommerce", "beat", "--loglevel=info"]
#         )
#         print("Celery Beat started.")

#         # Start ngrok (assuming your local server runs on port 8000)
#         ngrok_process = subprocess.Popen(["ngrok", "start_djangoserver"])
#         time.sleep(5)  # Wait for ngrok to initialize
#         print("ngrok started")
#         try:
#             super().handle(*args, **options)
#             print("All servers started successfully!")

#         finally:
#             redis_process.terminate()
#             celery_worker_process.terminate()
#             celery_beat_process.terminate()
#             ngrok_process.terminate()


class Command(RunserverCommand):
    """Start all servers"""

    help = "Start all extra servers: Redis, Celery worker, Celery Beat, and ngrok"

    def start_process(self, command, process_name):
        """Helper function to start a subprocess and print status."""
        try:
            process = subprocess.Popen(command)
            print(f"{process_name} started.")
            return process
        except Exception as e:
            print(f"Failed to start {process_name}: {e}")
            return None

    def handle(self, *args, **options):
        # Start Redis server
        redis_process = self.start_process(["redis-server"], "Redis server")

        # Start Celery worker
        celery_worker_process = self.start_process(
            ["celery", "-A", "ecommerce", "worker", "--loglevel=info"], "Celery worker"
        )

        # Start Celery Beat
        celery_beat_process = self.start_process(
            ["celery", "-A", "ecommerce", "beat", "--loglevel=info"], "Celery Beat"
        )

        # Register subprocess cleanup
        atexit.register(self.terminate_process, redis_process, "Redis server")
        atexit.register(self.terminate_process, celery_worker_process, "Celery worker")
        atexit.register(self.terminate_process, celery_beat_process, "Celery Beat")

        try:
            super().handle(*args, **options)
            print("Django server started, all processes running!")
        finally:
            # Processes will be terminated via atexit
            pass

    def terminate_process(self, process, process_name):
        """Terminate the given process."""
        if process and process.poll() is None:  # Check if process is still running
            print(f"Terminating {process_name}...")
            process.terminate()  # Use terminate() for graceful shutdown, or kill() for force
            try:
                process.wait(timeout=5)  # Wait a few seconds for graceful exit
            except subprocess.TimeoutExpired:
                print(f"Force killing {process_name}...")
                process.kill()
            print(f"{process_name} terminated.")
