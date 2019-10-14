TITLE
	SNDP_stochastic_MIP;

STOCHASTIC

SCENARIO
	SCEN := 1..3;

INDEX
	VAR_INDEX := (_A12, _B12, _A13, _B13, _A32, _A33, _C24, _C34) : 4;	! index should be created from 4 letters (avoid letter conflict)
	BIN_VAR_INDEX := (_C2, _C3) : 3;
	CONSTR_INDEX := 1..11;

PROBABILITIES
	Prob[SCEN] := (0.25, 0.5, 0.25);

DATA
	Cost[VAR_INDEX] := (2, 2, 2, 2, 1, 0, -11, -10);		!vector qT, transportation costs, selling price (signs are reverted in order to transform to MIN problem)
	Fixed_Cost[BIN_VAR_INDEX] := (2000, 2000);			!vector c, set up costs (signs are reverted in order to transform to MIN problem)
	T[CONSTR_INDEX, BIN_VAR_INDEX] := (	0,		0
						0,		0
						0,		0
						0,		0
						0,		0
						0,		0
						0,		0
						0,		0
						0,		0
						5000,		0
						0,		5000);	!matrix T (technological in 2 stage model)
	W[CONSTR_INDEX, VAR_INDEX] := (	1, 0, 0, 0, 1, 0, -2, 0,
					-1, 0, 0, 0, -1, 0, 2, 0,
					0, 0, 1, 0, 0, 1, 0, -2,
					0, 0, -1, 0, 0, -1, 0, 2,
					0, 1, 0, 0, 0, 0, -3, 0,
					0, -1, 0, 0, 0, 0, 3, 0,
					0, 0, 0, 1, 0, 0, 0, -3,
					0, 0, 0, -1, 0, 0, 0, 3,
					0, 0, 0, 0, 0, 0, -1, -1,
					0, 0, 0, 0, 0, 0, -1, 0,
					0, 0, 0, 0, 0, 0, 0, -1);	!matrix W (recourse in 2 stage model)
RANDOM DATA
	h[SCEN, CONSTR_INDEX] := (0, 0, 0, 0, 0, 0, 0, 0, -2000, 0, 0
				0, 0, 0, 0, 0, 0, 0, 0, -5000, 0, 0
				0, 0, 0, 0, 0, 0, 0, 0, -8000, 0, 0);

STAGE1 BINARY VARIABLES
	y[BIN_VAR_INDEX];

STAGE2 VARIABLES
	x[VAR_INDEX];

MIN									!MAX was transformed to MIN
	Objective = sum(BIN_VAR_INDEX: Fixed_Cost * y) + sum(VAR_INDEX: Cost * x);

SUBJECT TO
    	Constr[CONSTR_INDEX]: sum(VAR_INDEX: W * x) >= h - sum(BIN_VAR_INDEX: T * y);

END