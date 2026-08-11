import cProfile
import pstats

profiler = cProfile.Profile()

profiler.enable()

exec(open("main.py").read(), {"__name__": "__main__", "__file__": "main.py"})

profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.dump_stats("profcile.prof")
stats.print_stats(30)