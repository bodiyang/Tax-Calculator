"""
Translates TAXSIM-35 input file to Tax-Calculator tc input file.
"""
# CODING-STYLE CHECKS:
# pycodestyle prepare_tc_input.py
# pylint --disable=locally-disabled prepare_tc_input.py

import argparse
import os
import sys
import numpy as np
import pandas as pd


def main(file_in_name, file_out_name):
    """
    Translates TAXSIM-35 input file into a Tax-Calculator CSV-formatted
    tc input file. Any pre-existing OUTPUT file contents are overwritten.
    For details on Internet TAXSIM version 32 INPUT format, go to
    https://users.nber.org/~taxsim/taxsim35/

    Args:
        file_in_name (string): name of input file to run taxcalc with
        file_out_name (string): name of file to save taxcalc output to

    Returns:
        None
    """
    print("File in and out names: ", file_in_name, file_out_name)
    # check INPUT filename
    if not os.path.isfile(file_in_name):
        emsg = 'INPUT file named {} does not exist'.format(file_in_name)
        sys.stderr.write('ERROR: {}\n'.format(emsg))
        assert False
    # check OUTPUT filename
    if file_out_name == '':
        sys.stderr.write('ERROR: must specify OUTPUT file name\n')
        assert False
    if os.path.isfile(file_out_name):
        os.remove(file_out_name)
    # read TAXSIM-35 INPUT file into a pandas DataFrame
    ivar = pd.read_csv(file_in_name, delim_whitespace=True,
                       header=0, index_col=False, names=range(1, 33))
    # Drop 'idtl' – used to generate detailed output
    ivar.drop(columns=32)
    # translate INPUT variables into OUTPUT variables
    invar = translate(ivar)
    # write OUTPUT file containing Tax-Calculator input variables
    invar.to_csv(file_out_name, index=False)
    # return no-error exit code
    return 0
# end of main function code


def translate(ivar):
    """
    Translate TAXSIM-35 input variables into Tax-Calculator input variables.
    Both ivar and returned invar are pandas DataFrame objects.
    """
    assert isinstance(ivar, pd.DataFrame)
    invar = pd.DataFrame()
    invar['RECID'] = ivar.loc[:, 1]
    invar['FLPDYR'] = ivar.loc[:, 2]
    # no Tax-Calculator use of TAXSIM variable 3, state code
    mstat = ivar.loc[:, 4]
    assert np.all(np.logical_or(mstat == 1, mstat == 2))
    invar['age_head'] = ivar.loc[:, 5]
    invar['age_spouse'] = ivar.loc[:, 6]
    num_deps = ivar.loc[:, 7]
    mars = np.where(mstat == 1, np.where(num_deps > 0, 4, 1), 2)
    assert np.all(np.logical_or(mars == 1,
                                np.logical_or(mars == 2, mars == 4)))
    invar['MARS'] = mars
    invar['f2441'] = ivar.loc[:, 8]
    invar['n24'] = ivar.loc[:, 9]
    num_eitc_qualified_kids = ivar.loc[:, 10]
    invar['EIC'] = np.minimum(num_eitc_qualified_kids, 3)
    num_taxpayers = np.where(mars == 2, 2, 1)
    invar['XTOT'] = num_taxpayers + num_deps
    invar['e00200p'] = ivar.loc[:, 11]
    invar['e00200s'] = ivar.loc[:, 12]
    invar['e00200'] = invar['e00200p'] + invar['e00200s']
    invar['e00650'] = ivar.loc[:, 13]
    invar['e00600'] = invar['e00650']
    invar['e00300'] = ivar.loc[:, 14]
    invar['p22250'] = ivar.loc[:, 15]
    invar['p23250'] = ivar.loc[:, 16]
    invar['e02000'] = ivar.loc[:, 17]
    invar['e00800'] = ivar.loc[:, 18]
    invar['e01700'] = ivar.loc[:, 19]
    invar['e01500'] = invar['e01700']
    invar['e02400'] = ivar.loc[:, 20]
    invar['e02300'] = ivar.loc[:, 21]
    # no Tax-Calculator use of TAXSIM variable 22, non-taxable transfers
    # no Tax-Calculator use of TAXSIM variable 23, rent paid
    invar['e18500'] = ivar.loc[:, 24]
    invar['e18400'] = ivar.loc[:, 25]
    invar['e32800'] = ivar.loc[:, 26]
    invar['e19200'] = ivar.loc[:, 27]
    invar['e26270'] = ivar.loc[:, 28]
    invar['e00900p'] = ivar.loc[:, 29]
    invar['e00900s'] = ivar.loc[:, 31]
    invar['e00900'] = invar['e00900p'] + invar['e00900s']

    pprofinc = ivar.loc[:, 30]
    sprofinc = ivar.loc[:, 32]

    invar['PT_SSTB_income'] = 0#np.where(pprofinc + sprofinc > 0, 1, 0)
    invar['PT_SSTB_income'] = 0#np.where(invar['e26270'] > 0, 1, invar['PT_SSTB_income'])

    return invar


if __name__ == '__main__':
    sys.exit(main())
