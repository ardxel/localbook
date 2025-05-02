from abc import abstractmethod

from fastapi import FastAPI


class StaticComponent:
    def __init__(self, static_path: str) -> None:
        self.__static_path = static_path

    @property
    def static_path(self) -> str:
        return self.__static_path

    @abstractmethod
    def mount(self, app: FastAPI) -> None:
        raise NotImplementedError
