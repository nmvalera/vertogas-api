from celery import Celery, signature

from .common.config import config
from .tokens.constants import TOKEN_TASKS
from .web3.constants import WEB_TASKS
from .common.constants import MAIN_TASKS, TASK_UPDATE_ALL_CONTRACTS

app = Celery(
    config.CELERY_MODULE_NAME,
    include=WEB_TASKS + TOKEN_TASKS + MAIN_TASKS
)

app.config_from_object(config)


@app.on_after_configure.connect
def setup_periodic_tasks(sender):
    sender.add_periodic_task(10.0, signature(TASK_UPDATE_ALL_CONTRACTS), name='update logs every 10 seconds')
