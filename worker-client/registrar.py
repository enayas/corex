# worker-client/registrar.py
# worker introduces itself to the orchestrator
import httpx, config
from shared.schemas import WorkerRegister

async def register():
    payload = WorkerRegister(
        worker_id=config.WORKER_ID,
        webhook_url=f"http://{get_local_ip()}:{config.WEBHOOK_PORT}/jobs/incoming",
        region=config.REGION,
        cpu_cores=config.CPU_CORES,
        job_types=config.JOB_TYPES,
        min_payout_rate=config.MIN_PAYOUT_RATE
    )
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{config.ORCHESTRATOR_URL}/workers/register",
            json=payload.dict()
        )
    print(f"✓ Registered as {config.WORKER_ID}")

async def unregister():
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"{config.ORCHESTRATOR_URL}/workers/unregister/{config.WORKER_ID}"
        )

def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip