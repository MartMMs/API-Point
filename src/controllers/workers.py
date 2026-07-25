from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from datetime import date


from schemas.workers import WorkersIn, WorkersOut, WorkersUpdate, WorkerStatus
from security import login_required
from services.workers import WorkersService
from services.point import PointService
from schemas.point import PointOut, ReportOut


router = APIRouter(prefix="/workers", dependencies=[Depends(login_required)])


@router.get("/", response_model=list[WorkersOut])
async def read_workers(
    status: Optional[WorkerStatus] = Query(None, description="Filtrar por status. Se não for fornecido, retorna todos (ativos e inativos)."),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de funcionários a serem retornados."),
    skip: int = Query(0, ge=0, description="Número de funcionários a serem pulados (para paginação)."),
    workers_service: WorkersService = Depends()
):
    return await workers_service.read_all(status=status, limit=limit, skip=skip)

@router.get("/{worker_id}", response_model=WorkersOut)
async def read_worker_by_id(
    worker_id: int,
    workers_service: WorkersService = Depends()
):
    """Fetches a single worker by their ID."""
    worker = await workers_service.read_by_id(worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID {worker_id} not found."
        )
    return worker


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WorkersOut)
async def create_workers(
    worker: WorkersIn,
    workers_service: WorkersService = Depends()
):
    return await workers_service.create(worker)

@router.put("/{worker_id}", response_model=WorkersOut)
async def update_worker(
    worker_id: int,
    worker_data: WorkersUpdate,
    workers_service: WorkersService = Depends()
):
    """Updates an existing worker's data."""
    updated_worker = await workers_service.update(worker_id, worker_data)

    if not updated_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found."
        )
    return updated_worker


@router.get("/{id}/point", response_model=list[PointOut])
async def read_workers_point(
    id: int,
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros de ponto a serem retornados."),
    skip: int = Query(0, ge=0, description="Número de registros a serem pulados (para paginação)."),
    point_service: PointService = Depends()
):
    return await point_service.read_all_by_worker(worker_id=id, limit=limit, skip=skip)

@router.get("/{worker_id}/report", response_model=ReportOut, summary="Gera relatório de horas")
async def get_worker_report(
    worker_id: int,
    start_date: date = Query(..., description="Data de início do período (AAAA-MM-DD)"),
    end_date: date = Query(..., description="Data de fim do período (AAAA-MM-DD)"),
    point_service: PointService = Depends()
):
    """
    Generates a report of hours worked, overtime, and time balance
    for a worker in a specific period.
    """
    report = await point_service.generate_report(worker_id, start_date, end_date)
    if not report or not report["daily_summaries"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No days with closed shifts found for worker ID {worker_id} in the specified period."
        )
    return report

@router.delete("/{worker_id}", status_code=status.HTTP_200_OK, summary="Inativa ou deleta um funcionário")
async def delete_worker_endpoint(
    worker_id: int,
    force: bool = Query(False, description="Se 'true', deleta o registro permanentemente do banco de dados."),
    workers_service: WorkersService = Depends()
):
    """
    - By default (force=false), changes the worker's status to 'inactive' (soft delete).
    - With the `force=true` parameter, it permanently removes the worker from the system (hard delete).
    """
    if force:
        deleted = await workers_service.delete(worker_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found for deletion.")
        return {"detail": f"Worker with ID {worker_id} has been permanently deleted."}
    else:
        inactivated_worker = await workers_service.set_status(worker_id, WorkerStatus.inactive)
        if not inactivated_worker:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found for deactivation.")
        return {"detail": f"Worker with ID {worker_id} has been successfully deactivated."}