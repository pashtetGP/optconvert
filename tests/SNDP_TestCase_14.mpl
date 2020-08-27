!Properties from TestCase_0 that are present in this test case:
! - no matrix A
! - only bin vars on the first stage
! - standard bounds for 1st stage cont vars (if any)
! - only vector rhs is stochastic

!Properties specific for this TestCase:
! all scenarios have the same RHS
! integer vars on the 2nd stage

!These properties of are present in all TestCases:
! - MIN obj - always the case for smps files
! - 2 stages - only such problems are in scope of the research
! - only cont vars on the 2nd stage - we will solve the relaxation otherwise
! - >= constraints in subproblems - we do not care about subproblems
! - bin and cont (if any) vars on the first - int vars are prohibited

! Solution value: -17600
! Solution value 2nd stage relaxation: -17600.4
! Solution value all stages relaxation: -17900.1

TITLE
	SNDP_TestCase_14;

STOCHASTIC

SCENARIO
	SCEN := 1..3;

PROBABILITIES
	Prob[SCEN] := (0.25, 0.5, 0.25);

RANDOM DATA
	Demand[SCEN] := (5000, 5000, 5000);

STAGE1 INTEGER VARIABLES
	yc2;
	yc3;

STAGE2 VARIABLES
	x_c24;
	x_c34;
	x_a12;
	x_b12;
	x_a13;

STAGE2 INTEGER VARIABLES
	x_b13;
	x_a32;
	x_a33;

MIN	! should be min for solver
	- 13*(x_c24 + x_c34) + 2*x_a12 + 2*x_b12 + 2*x_a13 + 2*x_b13 + 1*x_a32 + 2*x_c24 + 3*x_c34 + 2000*yc2 + 2000*yc3;

SUBJECT TO
	x_a12 + x_a32 >= 2*x_c24;
	-x_a12 + -x_a32 >= -2*x_c24;

	x_a13 + x_a33 >= 2*x_c34;
	-x_a13 + -x_a33 >= -2*x_c34;

	x_b12 >= 3*x_c24;
	-x_b12 >= -3*x_c24;

	x_b13 >= 3*x_c34;
	-x_b13 >= -3*x_c34;

	-x_c24 >= -5000*yc2;
	-x_c34 >= -5000*yc3;
	-x_c24 + -x_c34 >= -Demand;

	-x_b13 + -x_a33 >= -24500.5; ! in the original problem these vars get 15K and 10K values

BOUNDS
	!x_b13 <= 100000;  ! integer should have UB to be treated as not binary in MPS
	!x_a32 <= 100000;
	!x_a33 <= 100000;
	yc2 <= 1;
	yc3 <= 1;
END