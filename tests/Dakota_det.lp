\   
\   Dakota_det.lp
\   
\   Generated with the MPL Modeling System
\   Copyright (c) 1988-2018  Maximal Software
\   
\   Date:               October 14, 2019
\   Time:               17:26
\   
\   Constraints:        6
\   Variables:          10
\   Integers:           7
\   Nonzeros:           15
\   Density:            25 %
\   


MAXIMIZE
  Profit:  BinVecDes + BinVecTab + BinVecCha - 2 PurchaseLum
     - 4 PurchaseFin - 5.2 PurchaseCar + 60 ProductionDes
     + 40 ProductionTab + 10 ProductionCha + BinaryVar

SUBJECT TO
  ResourceConstLum:   - PurchaseLum + 8 ProductionDes + 6 ProductionTab
     + ProductionCha  <=  0
  - PurchaseFin + 4 ProductionDes + 2 ProductionTab
     + 1.5 ProductionCha  <=  0
  ResourceConstCar:   - PurchaseCar + 2 ProductionDes
     + 1.5 ProductionTab + 0.5 ProductionCha  <=  0
  DemandConstraDes:   ProductionDes  <=  150
  DemandConstraTab:   ProductionTab  <=  125
  DemandConstraCha:   ProductionCha  <=  300

BOUNDS
    PurchaseLum FReE
    0 <= ProductionDes <= 160
    130 >= ProductionTab

INTEGERS
    ProductionDes
    ProductionTab
    ProductionCha

BINARY
    BinVecDes
    BinVecTab
    BinVecCha
    BinaryVar

END

