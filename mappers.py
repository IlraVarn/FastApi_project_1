from models import (Gate, 
                    GateStatus,
                    GateType,
                    GatePublic,
                    GateWithRequirementsPublic,
                    GateRequirementType,
                    GateRequirementPublic,
                    GateRequirement,
                    Organization,
                    OrganizationPublic)


    # Gate, 
    #                 GatePublic,
    #                 OrderItem, 
    #                 OrderItemPublic, 
    #                 OrderDetailWithItemsPublic,
    #                 OrderSummaryPerCustomerPublic,
    #                 CustomerWithOrdersPublic,
    #                 Organization, OrganizationPublic)
from sqlmodel import col

#customer helpers
# def to_customer_public(db_customer: Customer)-> CustomerPublic:
#     assert db_customer.id is not None

#     return CustomerPublic(
#         id=db_customer.id,
#         name= db_customer.name,
#         email=db_customer.email
#     )

# def to_customer_public_list(db_customers: list[Customer]
#                             )-> list[CustomerPublic]:
#     public_customers = []
#     for db_customer in db_customers:
#         public_customer = to_customer_public(db_customer)
#         public_customers.append(public_customer)

#     return public_customers


def to_gate_public(db_gate: Gate)-> GatePublic:
    assert db_gate.id is not None

    return GatePublic(
        id=db_gate.id,
        organization_id=db_gate.organization_id,
        gate_type=GateType(db_gate.gate_type),
        status=GateStatus(db_gate.status),
        created_at=db_gate.created_at,
        updated_at=db_gate.updated_at,
        archived_at=db_gate.archived_at,
        reference=db_gate.reference
    )



def to_gate_with_requirements_public(
        db_gate: Gate,
        db_requirements: list[GateRequirement]
        ) -> GateWithRequirementsPublic:
    
    assert db_gate.id is not None

    public_requirements = []

    for db_requirement in db_requirements:
        public_requirement = to_requirement_public(db_requirement)
        public_requirements.append(public_requirement)
    
    return GateWithRequirementsPublic(
        id=db_gate.id,
        organization_id=db_gate.organization_id,
        gate_type=GateType(db_gate.gate_type),
        status=GateStatus(db_gate.status),
        created_at=db_gate.created_at,
        updated_at=db_gate.updated_at,
        archived_at=db_gate.archived_at,
        reference=db_gate.reference,
        requirements=public_requirements
    )



def to_requirement_public_list(
        db_requirements: list[GateRequirement]
        )-> list[GateRequirementPublic]:
    
    public_requirements=[]
    for db_requirement in db_requirements:
        public_requirement= to_requirement_public(db_requirement)
        public_requirements.append(public_requirement)

    return public_requirements


def to_requirement_public(
        db_requirement: GateRequirement
    )-> GateRequirementPublic:
    
    assert db_requirement.id is not None

    return GateRequirementPublic(
        id=db_requirement.id,
        requirement_type=GateRequirementType(db_requirement.requirement_type),
        created_at=db_requirement.created_at
    )


def to_organization_public(db_organization: Organization) -> OrganizationPublic:
    assert db_organization.id is not None
    
    return OrganizationPublic(
        id= db_organization.id,
        name=db_organization.name,
    )






# def to_order_public_list(
#         db_orders: list[Order]
#         )-> list[OrderPublic]:
    
#     public_orders=[]
#     for db_order in db_orders:
#         public_order= to_order_public(db_order)
#         public_orders.append(public_order)

#     return public_orders







# def to_customer_with_orders_public(
#     db_customer: Customer,
#     db_orders: list[Order],
# ) -> CustomerWithOrdersPublic:
#     """Convert persisted customer and order records 
#     to the public response."""


#     public_orders: list[OrderSummaryPerCustomerPublic] = []

#     for db_order in db_orders:
#         assert db_order.id is not None

#         public_order = OrderSummaryPerCustomerPublic(
#             id=db_order.id,
#             created_at=db_order.created_at,
#             total_cents=db_order.total_cents,
#             status=db_order.status,
#         )

#         public_orders.append(public_order)

#     assert db_customer.id is not None

#     return CustomerWithOrdersPublic(
#         id=db_customer.id,
#         name=db_customer.name,
#         email=db_customer.email,
#         orders=public_orders,
#     )

