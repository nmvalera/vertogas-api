from celery import Celery, signature

from .common.config import config
from .common.constants import TASK_UPDATE_LISTENING_CONTRACTS


app = Celery(
    config.CELERY_MODULE_NAME,
    include=['app.tasks', 'app.tokens.tasks', 'app.web3.tasks']
)

app.config_from_object(config)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0,
                             signature(TASK_UPDATE_LISTENING_CONTRACTS, args=()),
                             name='update logs every 10 seconds')
