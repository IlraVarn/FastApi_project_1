from app.models import (
                    Organization,
                    OrganizationPublic,
                    )

from sqlmodel import col





def to_organization_public(db_organization: Organization) -> OrganizationPublic:
    assert db_organization.id is not None
    
    return OrganizationPublic(
        id= db_organization.id,
        name=db_organization.name,
    )

