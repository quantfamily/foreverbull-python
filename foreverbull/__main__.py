from foreverbull import Foreverbull
import foreverbull_core.logger
if __name__ == "__main__":
    foreverbull_core.logger.Logger().configure()
    fb = Foreverbull()
    fb.run()
