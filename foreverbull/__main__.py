import foreverbull_core.logger

from foreverbull import Foreverbull

if __name__ == "__main__":
    foreverbull_core.logger.Logger().configure()
    fb = Foreverbull()
    fb.run()
