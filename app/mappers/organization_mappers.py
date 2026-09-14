from app.models import (
                    Organization,
                    )
from app.schemas import OrganizationPublic
from sqlmodel import col
from app.errors import DataIntegrityError





def to_organization_public(db_organization: Organization) -> OrganizationPublic:

    if db_organization.id is None:
        raise DataIntegrityError()
    
    return OrganizationPublic(
        id= db_organization.id,
        name=db_organization.name,
    )

