You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.

REFORM DOCUMENTATION
Baseline Growth-Difference Assumption Values by Year:
none: using default baseline growth assumptions
Policy Reform Parameter Values by Year:
2020:
 _II_em : 1000
  name: Personal and dependent exemption amount
  desc: Subtracted from AGI in the calculation of taxable income, per taxpayer
        and dependent.
  baseline_value: 0.0
 _II_rt5 : 0.36
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 5
  desc: The third highest tax rate, applied to the portion of taxable income
        below tax bracket 5 and above tax bracket 4.
  baseline_value: 0.32
 _II_rt6 : 0.39
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 6
  desc: The second higher tax rate, applied to the portion of taxable income
        below tax bracket 6 and above tax bracket 5.
  baseline_value: 0.35
 _II_rt7 : 0.41
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 7
  desc: The tax rate applied to the portion of taxable income below tax
        bracket 7 and above tax bracket 6.
  baseline_value: 0.37
 _PT_rt5 : 0.36
  name: Pass-through income tax rate 5
  desc: The third highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 5
        and above tax bracket 4.
  baseline_value: 0.32
 _PT_rt6 : 0.39
  name: Pass-through income tax rate 6
  desc: The second higher tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 6
        and above tax bracket 5.
  baseline_value: 0.35
 _PT_rt7 : 0.41
  name: Pass-through income tax rate 7
  desc: The highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 7
        and above tax bracket 6.
  baseline_value: 0.37

2020_CLP_itax_rev($B)= 1432.600
2020_REF_itax_rev($B)= 1428.017

CLP diagnostic table:
                                     2020
Returns (#m)                      167.510
AGI ($b)                        12041.458
Itemizers (#m)                     31.240
Itemized Deduction ($b)           878.287
Standard Deduction Filers (#m)    136.270
Standard Deduction ($b)          2440.766
Personal Exemption ($b)             0.000
Taxable Income ($b)              9216.525
Regular Tax ($b)                 1592.841
AMT Income ($b)                 11424.323
AMT Liability ($b)                  1.374
AMT Filers (#m)                     0.260
Tax before Credits ($b)          1594.215
Refundable Credits ($b)            78.050
Nonrefundable Credits ($b)         93.997
Reform Surtaxes ($b)                0.000
Other Taxes ($b)                   10.432
Ind Income Tax ($b)              1432.600
Payroll Taxes ($b)               1327.653
Combined Liability ($b)          2760.253
With Income Tax <= 0 (#m)          60.120
With Combined Tax <= 0 (#m)        39.120

REF diagnostic table:
                                     2020
Returns (#m)                      167.510
AGI ($b)                        12041.458
Itemizers (#m)                     31.170
Itemized Deduction ($b)           876.211
Standard Deduction Filers (#m)    136.340
Standard Deduction ($b)          2442.096
Personal Exemption ($b)           333.334
Taxable Income ($b)              8963.931
Regular Tax ($b)                 1585.819
AMT Income ($b)                 11426.046
AMT Liability ($b)                  1.376
AMT Filers (#m)                     0.260
Tax before Credits ($b)          1587.196
Refundable Credits ($b)            80.781
Nonrefundable Credits ($b)         88.829
Reform Surtaxes ($b)                0.000
Other Taxes ($b)                   10.432
Ind Income Tax ($b)              1428.017
Payroll Taxes ($b)               1327.653
Combined Liability ($b)          2755.670
With Income Tax <= 0 (#m)          62.370
With Combined Tax <= 0 (#m)        39.450

Extract of 2020 distribution table by baseline expanded-income decile:
        funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0-10n         0.05      0.006      0.007            -13.155            -13.155
0-10z         0.93      0.000      0.000             -0.000             -0.000
0-10p        15.77     -4.280     -4.640            176.760            177.120
10-20        16.75     -1.652     -2.722            414.305            415.375
20-30        16.75      3.181      1.960            552.887            554.108
30-40        16.75     10.215      8.523            680.590            682.281
40-50        16.75     19.433     17.080            839.476            841.829
50-60        16.75     33.452     30.355           1031.334           1034.432
60-70        16.75     62.384     58.428           1269.639           1273.595
70-80        16.75    108.746    103.384           1592.696           1598.057
80-90        16.75    217.842    209.539           2121.011           2129.315
90-100       16.75    983.272   1006.102           4335.353           4312.523
ALL         167.51   1432.600   1428.017          13000.897          13005.480
90-95         8.38    217.863    213.571           1449.125           1453.417
95-99         6.70    331.552    330.100           1680.139           1681.591
Top 1%        1.68    433.857    462.431           1206.090           1177.515

Extract of 2020 income-tax difference table by expanded-income decile:
        funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0-10n         0.05         0.000           2.9                  0.0
0-10z         0.93         0.000           0.0                  0.0
0-10p        15.77        -0.360         -22.8                  0.2
10-20        16.75        -1.070         -63.9                  0.3
20-30        16.75        -1.220         -72.9                  0.2
30-40        16.75        -1.691        -101.0                  0.2
40-50        16.75        -2.353        -140.4                  0.3
50-60        16.75        -3.098        -184.9                  0.3
60-70        16.75        -3.957        -236.2                  0.3
70-80        16.75        -5.361        -320.0                  0.3
80-90        16.75        -8.303        -495.7                  0.4
90-100       16.75        22.830        1362.9                 -0.5
ALL         167.51        -4.583         -27.4                  0.0
90-95         8.38        -4.292        -512.5                  0.3
95-99         6.70        -1.452        -216.7                  0.1
Top 1%        1.68        28.574       17057.9                 -2.4
