TITLE
    
    DakotaModel_deterministic;
    ! Objective value 4165.0
    ! line 23 has a syntax error

INDEX

    PRODUCTS := (Desk, Table, Chair);
    RESOURCES := (Lumber, Finishing, Carpentry);

DATA

    Price[PRODUCTS] := (60, 40, 10);
    Cost[RESOURCES] := (2, 4, 5.2);
    Consumption[RESOURCES, PRODUCTS] := (8, 6, 1
					4, 2, 1.5
					2, 1.5, .5);
    Demand[PRODUCTS] := (150, 125, 300);

INTEGER VARIABLES

   ProductionPRODUCTS];

VARIABLES

   Purchase[RESOURCES];

MAX

    Profit = sum(PRODUCTS: Price * Production) - sum(RESOURCES: Cost * Purchase);

SUBJECT TO

    ResourceConstraint[RESOURCES]: sum(PRODUCTS: Consumption * Production) <= Purchase;
    DemandConstraint[PRODUCTS]: Production <= Demand;

END