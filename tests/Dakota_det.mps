*   
*   Dakota_det.mps
*   
*   Generated with the MPL Modeling System
*   Copyright (c) 1988-2018  Maximal Software
*   
*   Date:               October 14, 2019
*   Time:               16:32
*   
*   Constraints:        6
*   Variables:          10
*   Integers:           7
*   Nonzeros:           15
*   Density:            25 %
*   
NAME          Dakota_det.lp (MIN)
ROWS
  N Profit
  L ResourceConstLum
  L ResourceConstFin
  L ResourceConstCar
  L DemandConstraDes
  L DemandConstraTab
  L DemandConstraCha
COLUMNS
    INTEGERS  'MARKER'                 'INTORG'
    ProductionDes  Profit           -60.0   ResourceConstLum           8.0
    ProductionDes  ResourceConstFin           4.0   ResourceConstCar           2.0
    ProductionDes  DemandConstraDes           1.0
    ProductionTab  Profit           -40.0   ResourceConstLum           6.0
    ProductionTab  ResourceConstFin           2.0   ResourceConstCar           1.5
    ProductionTab  DemandConstraTab           1.0
    ProductionCha  Profit           -10.0   ResourceConstLum           1.0
    ProductionCha  ResourceConstFin           1.5   ResourceConstCar           0.5
    ProductionCha  DemandConstraCha           1.0
    INTEGERE  'MARKER'                 'INTEND'
    BinaryVar  Profit            -1.0
    BinaryVecDes  Profit            -1.0
    BinaryVecTab  Profit            -1.0
    BinaryVecCha  Profit            -1.0
    PurchaseLum  Profit             2.0   ResourceConstLum          -1.0
    PurchaseFin  Profit             4.0   ResourceConstFin          -1.0
    PurchaseCar  Profit             5.2   ResourceConstCar          -1.0
RHS
    RHS1      DemandConstraDes         150.0   DemandConstraTab         125.0
    RHS1      DemandConstraCha         300.0
BOUNDS
 UP BOUND1    ProductionDes         160.0
 UP BOUND1    ProductionTab         130.0
 UP BOUND1    ProductionCha       32000.0
 BV BOUND1    BinaryVar           1.0
 BV BOUND1    BinaryVecDes           1.0
 BV BOUND1    BinaryVecTab           1.0
 BV BOUND1    BinaryVecCha           1.0
 FR BOUND1    PurchaseLum
ENDATA


