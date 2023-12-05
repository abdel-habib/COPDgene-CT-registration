def format_elapsed_time(start_time, end_time):
    elapsed_time_seconds = end_time - start_time

    elapsed_minutes = int(elapsed_time_seconds // 60)
    elapsed_seconds = int(elapsed_time_seconds % 60)

    return elapsed_minutes, elapsed_seconds

