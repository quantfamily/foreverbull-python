import requests


class RequestError(Exception):
    pass


class Service:
    def __init__(self, host):
        self.host = host

    def list_services(self):
        rsp = requests.get(f"http://{self.host}:8080/services")
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def create_service(self, service):
        rsp = requests.post(f"http://{self.host}:8080/services", json=service)
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def get_service(self, service_id):
        rsp = requests.get(f"http://{self.host}:8080/services/{service_id}")
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def update_service():
        pass

    def delete_service(self, service_id):
        rsp = requests.delete(f"http://{self.host}:8080/services/{service_id}")
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return True

    def list_instances(self, service_id):
        rsp = requests.get(f"http://{self.host}:8080/services/{service_id}/instances")
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def create_instance(self, service_id, instance):
        rsp = requests.post(
            f"http://{self.host}:8080/services/{service_id}/instances", json=instance
        )
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def get_instance(self, service_id, instance_id):
        rsp = requests.get(
            f"http://{self.host}:8080/services/{service_id}/instances/{instance_id}"
        )
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def update_instance():
        pass

    def delete_instance(self, service_id, instance_id):
        rsp = requests.delete(
            f"http://{self.host}:8080/services/{service_id}/instances/{instance_id}"
        )
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return True

    def list_containers(self):
        rsp = requests.get(f"http://http://{self.host}:8080/services/containers")
        if not rsp.ok:
            raise RequestError(
                f"http://http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def create_container(self, container):
        rsp = requests.post(
            f"http://{self.host}:8080/services/containers", json=container
        )
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def get_container(self, container_id):
        rsp = requests.get(
            f"http://{self.host}:8080/services/containers/{container_id}"
        )
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def update_container():
        pass

    def delete_container(self, container_id):
        rsp = requests.delete(
            f"http://{self.host}:8080/services/containers/{container_id}"
        )
        if not rsp.ok:
            raise RequestError(
                f"http://call to services gave bad return code: {rsp.status_code}"
            )
        return True
