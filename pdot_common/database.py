"""
Database helper methods
"""
from tortoise import Tortoise, connections

from pdot_common.info import Info


class Database(object):
    """
    Database connection singleton class
    """

    initialized = False

    def __init__(self, initialize=False):
        if not Database.initialized and not initialize:
            raise Exception("Database connection not initialized")

    @staticmethod
    def conn_str():
        info = Info()

        return f"postgres://{info.db_user()}:{info.db_password()}@{info.db_host()}:{info.db_port()}/{info.db_name()}"

    async def init(self, models):
        if Database.initialized:
            return
        await Tortoise.init(
            db_url=self.conn_str(), use_tz=True, modules={"models": models}
        )

        self.initialized = True

    async def shutdown(self):
        await connections.close_all()
        self.initialized = False
