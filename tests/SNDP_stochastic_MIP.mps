*   
*   SNDP_stochastic_MIP.mps
*   
*   Generated with the MPL Modeling System
*   Copyright (c) 1988-2018  Maximal Software
*   
*   Date:               October 14, 2019
*   Time:               18:39
*   
*   Constraints:        11
*   Variables:          10
*   Integers:           2
*   Nonzeros:           26
*   Density:            24 %
*   
NAME          SNDP_stochastic_MIP (MIN)
ROWS
  N Objective
  G Constr01
  G Constr02
  G Constr03
  G Constr04
  G Constr05
  G Constr06
  G Constr07
  G Constr08
  G Constr09
  G Constr10
  G Constr11
COLUMNS
    y_C2      Objective        2000.0   Constr10        5000.0
    y_C3      Objective        2000.0   Constr11        5000.0
    x_A12     Objective           2.0   Constr01           1.0
    x_A12     Constr02          -1.0
    x_B12     Objective           2.0   Constr05           1.0
    x_B12     Constr06          -1.0
    x_A13     Objective           2.0   Constr03           1.0
    x_A13     Constr04          -1.0
    x_B13     Objective           2.0   Constr07           1.0
    x_B13     Constr08          -1.0
    x_A32     Objective           1.0   Constr01           1.0
    x_A32     Constr02          -1.0
    x_A33     Objective           0.0   Constr03           1.0
    x_A33     Constr04          -1.0
    x_C24     Objective         -11.0   Constr01          -2.0
    x_C24     Constr02           2.0   Constr05          -3.0
    x_C24     Constr06           3.0   Constr09          -1.0
    x_C24     Constr10          -1.0
    x_C34     Objective         -10.0   Constr03          -2.0
    x_C34     Constr04           2.0   Constr07          -3.0
    x_C34     Constr08           3.0   Constr09          -1.0
    x_C34     Constr11          -1.0
RHS
    RHS1      Constr09       -2000.0
BOUNDS
 BV BOUND1    y_C2               1.0
 BV BOUND1    y_C3               1.0
*
TIME          SNDP_stochastic_MIP (MIN)
PERIODS       IMPLICIT
    y_C2      Constr01                 Stage1    
    x_A12     Constr01                 Stage2    
*
STOCH         SNDP_stochastic_MIP (MIN)
SCENARIOS
 SC Scen1     'ROOT'            0.25   Stage1    
    RHS1      Constr09       -2000.0
 SC Scen2     Scen1              0.5   Stage2    
    RHS1      Constr09       -5000.0
 SC Scen3     Scen1             0.25   Stage2    
    RHS1      Constr09       -8000.0
ENDATA


