"""Doris SQL connection shared by the warehouse scripts."""

import os

import pymysql

DATABASE = "cappy_vk_lsvd_3w"


def connection(*, client_flag=0, select_database=True):
    return pymysql.connect(
        host=os.environ["VK_DORIS_HOST"],
        port=int(os.environ["VK_DORIS_PORT"]),
        user=os.environ["VK_DORIS_USER"],
        password=os.environ["VK_DORIS_PASSWORD"],
        database=DATABASE if select_database else None,
        autocommit=True,
        client_flag=client_flag,
        read_timeout=1800,
    )
