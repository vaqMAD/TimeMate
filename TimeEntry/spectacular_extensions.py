from drf_spectacular.extensions import OpenApiFilterExtension


class TimeEntryFilterExtension(OpenApiFilterExtension):
    target_class = 'TimeEntry.filters.TimeEntryFilter'
    match_subclasses = True