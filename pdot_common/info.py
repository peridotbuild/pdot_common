"""
Application information
"""
import os

from pdot_common.env import get_env, is_k8s


class Info:
    """
    Application information singleton class
    """

    _name = None
    _dbname = None

    def __init__(self, name=None, dbname=None):
        if not self._name and not name:
            raise ValueError("Info.name is not set")
        if self._name and name:
            raise ValueError("Info.name is already set")
        if name:
            Info._name = name
            Info._dbname = dbname if dbname else name

        self._name = Info._name

    def name(self):
        return self._name

    def db_name(self):
        return f"{self._dbname}{get_env()}"

    @staticmethod
    def db_user():
        return os.environ.get("DB_USER", "postgres")

    @staticmethod
    def db_password():
        return os.environ.get("DB_PASSWORD", "postgres")

    @staticmethod
    def db_host():
        return os.environ.get("DB_HOST", "localhost")

    @staticmethod
    def db_port():
        return os.environ.get("DB_PORT", "5432")

    @staticmethod
    def db_ssl_mode():
        return os.environ.get("DB_SSLMODE", "disable")

    @staticmethod
    def temporal_host():
        if is_k8s():
            return os.environ.get(
                "TEMPORAL_HOSTPORT",
                "workflow-temporal-frontend.workflow.svc.cluster.local:7233",
            )
        else:
            return os.environ.get("TEMPORAL_HOSTPORT", "localhost:7233")

    @staticmethod
    def temporal_namespace():
        return os.environ.get("TEMPORAL_NAMESPACE", "default")
