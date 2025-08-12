"""
Document management endpoints
"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import Documento, Usuario, PerfilEnum
from app.core.deps import (
    get_current_user, require_admin, PermissionChecker, log_action
)
from app.core.config import settings
from app.schemas.documento import (
    DocumentoResponse, DocumentoListResponse, DocumentoFilter
)

router = APIRouter()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # Check file extension
    if file.filename:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )


async def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    """Save uploaded file and return file path and URL"""
    # Create user directory
    user_dir = os.path.join(settings.UPLOAD_PATH, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(user_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Generate URL (relative to upload path)
    file_url = f"/uploads/{user_id}/{unique_filename}"
    
    return file_path, file_url


@router.get("/", response_model=DocumentoListResponse)
async def list_documentos(
    request: Request,
    filter_params: DocumentoFilter = Depends(),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List documents with pagination and filters
    Users can only see their own documents unless they are admin/supervisor
    """
    # Build base query
    query = select(Documento).options(selectinload(Documento.usuario))
    
    # Apply user restrictions
    conditions = []
    if current_user.perfil == PerfilEnum.SOCIO:
        conditions.append(Documento.usuario_id == current_user.id)
    elif filter_params.usuario_id:
        conditions.append(Documento.usuario_id == filter_params.usuario_id)
    
    # Apply filters
    if filter_params.tipo_documento:
        conditions.append(Documento.tipo_documento == filter_params.tipo_documento)
    
    if filter_params.processado is not None:
        conditions.append(Documento.processado == filter_params.processado)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count total
    count_query = select(func.count(Documento.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (filter_params.page - 1) * filter_params.per_page
    query = query.offset(offset).limit(filter_params.per_page)
    query = query.order_by(Documento.data_upload.desc())
    
    # Execute query
    result = await db.execute(query)
    documentos = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_DOCUMENTOS",
        details={"filters": filter_params.dict()},
        db=db
    )
    
    # Calculate pagination
    pages = (total + filter_params.per_page - 1) // filter_params.per_page
    
    return DocumentoListResponse(
        documentos=[DocumentoResponse.from_orm(doc) for doc in documentos],
        total=total,
        page=filter_params.page,
        per_page=filter_params.per_page,
        pages=pages
    )


@router.get("/{documento_id}", response_model=DocumentoResponse)
async def get_documento(
    documento_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get document by ID
    Users can only view their own documents
    """
    # Get document
    result = await db.execute(
        select(Documento)
        .options(selectinload(Documento.usuario))
        .where(Documento.id == documento_id)
    )
    documento = result.scalar_one_or_none()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, documento.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this document"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_DOCUMENTO",
        resource="Documento",
        resource_id=documento_id,
        db=db
    )
    
    return DocumentoResponse.from_orm(documento)


@router.post("/upload", response_model=DocumentoResponse)
async def upload_documento(
    request: Request,
    tipo_documento: str,
    usuario_id: Optional[int] = None,
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload document
    Users can upload their own documents, admins can upload for any user
    """
    # Determine target user
    target_user_id = usuario_id if usuario_id else current_user.id
    
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, target_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload document for this user"
        )
    
    # Validate file
    validate_file(file)
    
    # Verify target user exists
    if target_user_id != current_user.id:
        result = await db.execute(
            select(Usuario).where(Usuario.id == target_user_id)
        )
        target_user = result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
    
    # Save file
    file_path, file_url = await save_uploaded_file(file, target_user_id)
    
    # Create document record
    documento = Documento(
        usuario_id=target_user_id,
        tipo_documento=tipo_documento,
        nome_arquivo=file.filename or "unknown",
        arquivo_url=file_url,
        arquivo_path=file_path,
        tamanho_bytes=file.size if hasattr(file, 'size') else None,
        mime_type=file.content_type,
        processado=False
    )
    
    db.add(documento)
    await db.commit()
    await db.refresh(documento, ['usuario'])
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPLOAD_DOCUMENTO",
        resource="Documento",
        resource_id=documento.id,
        details={
            "tipo_documento": tipo_documento,
            "filename": file.filename,
            "target_user_id": target_user_id
        },
        db=db
    )
    
    # TODO: Trigger OCR/NLP processing with Celery
    # from app.services.document_processor import process_document_task
    # process_document_task.delay(documento.id)
    
    return DocumentoResponse.from_orm(documento)


@router.get("/{documento_id}/download")
async def download_documento(
    documento_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download document file
    Users can only download their own documents
    """
    # Get document
    result = await db.execute(
        select(Documento).where(Documento.id == documento_id)
    )
    documento = result.scalar_one_or_none()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, documento.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to download this document"
        )
    
    # Check if file exists
    if not documento.arquivo_path or not os.path.exists(documento.arquivo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="DOWNLOAD_DOCUMENTO",
        resource="Documento",
        resource_id=documento_id,
        db=db
    )
    
    return FileResponse(
        path=documento.arquivo_path,
        filename=documento.nome_arquivo,
        media_type=documento.mime_type or 'application/octet-stream'
    )


@router.delete("/{documento_id}")
async def delete_documento(
    documento_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete document
    Users can delete their own documents, admins can delete any
    """
    # Get document
    result = await db.execute(
        select(Documento).where(Documento.id == documento_id)
    )
    documento = result.scalar_one_or_none()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, documento.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this document"
        )
    
    # Delete physical file
    if documento.arquivo_path and os.path.exists(documento.arquivo_path):
        try:
            os.remove(documento.arquivo_path)
        except OSError:
            pass  # File might be already deleted or locked
    
    # Delete database record
    await db.delete(documento)
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="DELETE_DOCUMENTO",
        resource="Documento",
        resource_id=documento_id,
        details={"filename": documento.nome_arquivo},
        db=db
    )
    
    return {"message": "Document deleted successfully"}


@router.post("/{documento_id}/process")
async def trigger_document_processing(
    documento_id: int,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger document OCR/NLP processing
    Only admins can trigger processing
    """
    # Get document
    result = await db.execute(
        select(Documento).where(Documento.id == documento_id)
    )
    documento = result.scalar_one_or_none()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if file exists
    if not documento.arquivo_path or not os.path.exists(documento.arquivo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="TRIGGER_PROCESSING",
        resource="Documento",
        resource_id=documento_id,
        db=db
    )
    
    # TODO: Trigger OCR/NLP processing with Celery
    # from app.services.document_processor import process_document_task
    # task = process_document_task.delay(documento_id)
    # return {"message": "Processing started", "task_id": task.id}
    
    return {"message": "Processing triggered (not implemented yet)"}


@router.get("/user/{user_id}", response_model=List[DocumentoResponse])
async def get_user_documentos(
    user_id: int,
    request: Request,
    tipo_documento: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents for a specific user
    """
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user's documents"
        )
    
    # Build query
    conditions = [Documento.usuario_id == user_id]
    if tipo_documento:
        conditions.append(Documento.tipo_documento == tipo_documento)
    
    query = select(Documento).options(selectinload(Documento.usuario)).where(
        and_(*conditions)
    ).order_by(Documento.data_upload.desc())
    
    result = await db.execute(query)
    documentos = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_USER_DOCUMENTOS",
        details={"user_id": user_id, "tipo_documento": tipo_documento},
        db=db
    )
    
    return [DocumentoResponse.from_orm(doc) for doc in documentos]


@router.get("/types/available")
async def get_available_document_types():
    """
    Get list of available document types
    """
    # In production, this might come from a configuration table
    document_types = [
        {"code": "RG", "name": "RG - Registro Geral", "required": True},
        {"code": "CPF", "name": "CPF - Cadastro de Pessoa Física", "required": True},
        {"code": "CNES", "name": "CNES - Cadastro Nacional de Estabelecimentos de Saúde", "required": True},
        {"code": "CRM", "name": "CRM - Conselho Regional de Medicina", "required": False},
        {"code": "COREN", "name": "COREN - Conselho Regional de Enfermagem", "required": True},
        {"code": "TITULO_ELEITOR", "name": "Título de Eleitor", "required": False},
        {"code": "COMPROVANTE_RESIDENCIA", "name": "Comprovante de Residência", "required": True},
        {"code": "CURRICULUM", "name": "Currículo Profissional", "required": False},
        {"code": "CERTIFICADOS", "name": "Certificados e Diplomas", "required": False},
        {"code": "FOTO_3x4", "name": "Foto 3x4", "required": True},
    ]
    
    return {"document_types": document_types}


@router.get("/stats/summary")
async def get_document_stats(
    request: Request,
    usuario_id: Optional[int] = Query(None),
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get document statistics
    Only admins can view stats
    """
    # Build conditions
    conditions = []
    if usuario_id:
        conditions.append(Documento.usuario_id == usuario_id)
    
    # Get stats
    stats_query = select(
        func.count(Documento.id).label('total'),
        func.count(func.nullif(Documento.processado == True, False)).label('processados'),
        func.count(func.nullif(Documento.processado == False, False)).label('pendentes'),
        func.count(func.distinct(Documento.usuario_id)).label('usuarios_com_docs')
    )
    
    if conditions:
        stats_query = stats_query.where(and_(*conditions))
    
    result = await db.execute(stats_query)
    stats = result.first()
    
    # Get document type distribution
    type_query = select(
        Documento.tipo_documento,
        func.count(Documento.id).label('count')
    ).group_by(Documento.tipo_documento)
    
    if conditions:
        type_query = type_query.where(and_(*conditions))
    
    type_result = await db.execute(type_query)
    type_distribution = {row.tipo_documento: row.count for row in type_result}
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_DOCUMENT_STATS",
        details={"usuario_id": usuario_id},
        db=db
    )
    
    return {
        "total_documentos": stats.total or 0,
        "processados": stats.processados or 0,
        "pendentes": stats.pendentes or 0,
        "usuarios_com_documentos": stats.usuarios_com_docs or 0,
        "distribuicao_por_tipo": type_distribution
    } 