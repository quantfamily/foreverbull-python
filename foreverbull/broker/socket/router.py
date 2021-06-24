from collections import namedtuple

import foreverbull

ROUTE = namedtuple("route", "func, route, model")


class TaskNotFoundError(Exception):
    pass


class MessageRouter:
    def __init__(self):
        self._logger = foreverbull.get_logger("feed")
        self._routes = {}

    def __call__(self, data):
        request = foreverbull.models.Request.load(data)
        if request.task not in self._routes:
            return foreverbull.models.Response(
                task=request.task, error=repr(TaskNotFoundError("not found"))
            ).dump()
        route = self._routes[request.task]
        try:
            if route.model is None:
                data = route.func()
            else:
                model_data = route.model.load(request.data)
                data = route.func(model_data)
            response = foreverbull.models.Response(task=request.task, data=data)
        except Exception as exc:
            self._logger.error(f"Error calling task: {request.task}")
            self._logger.error(exc, exc_info=True)
            response = foreverbull.models.Response(task=request.task, error=str(exc))
        return response.dump()

    def add_route(self, function, route, model=None):
        new_route = ROUTE(function, route, model)
        self._routes[route] = new_route
