"""
Tax-Calculator abstract base parameters class.
"""
# CODING-STYLE CHECKS:
# pycodestyle parameters.py
# pylint --disable=locally-disabled parameters.py
#
# pylint: disable=attribute-defined-outside-init,no-member

import os
import abc
import numpy as np
from taxcalc.utils import read_egg_json, json_to_dict


class Parameters():
    """
    Inherit from this class for Policy, Consumption, GrowDiff, and
    other groups of parameters that need to have a set_year method.
    Override this __init__ method and DEFAULTS_FILE_NAME and
    DEFAULTS_FILE_PATH in the inheriting class.
    """
    __metaclass__ = abc.ABCMeta

    DEFAULTS_FILE_NAME = None
    DEFAULTS_FILE_PATH = None

    def __init__(self):
        pass

    def initialize(self, start_year, num_years):
        """
        Called from subclass __init__ function.
        """
        self._current_year = start_year
        self._start_year = start_year
        self._num_years = num_years
        self._end_year = start_year + num_years - 1
        self.set_default_vals()

    def inflation_rates(self):
        """
        Override this method in subclass when appropriate.
        """
        # pylint: disable=no-self-use
        return None

    def wage_growth_rates(self):
        """
        Override this method in subclass when appropriate.
        """
        # pylint: disable=no-self-use
        return None

    def indexing_rates(self, param_name):
        """
        Return appropriate indexing rates for specified param_name.
        """
        if param_name in ('_SS_Earnings_c', '_SS_Earnings_thd'):
            return self.wage_growth_rates()
        return self.inflation_rates()

    def set_default_vals(self, known_years=999999):
        """
        Called by initialize method and from some subclass methods.
        """
        # pylint: disable=too-many-nested-blocks
        if isinstance(known_years, int):
            known_years_is_int = True
        elif isinstance(known_years, dict):
            known_years_is_int = False
        else:
            raise ValueError('known_years is neither an int nor a dict')
        if hasattr(self, '_vals'):
            for name, data in self._vals.items():
                valtype = data.get('value_type')
                values = data.get('value')
                if values:
                    cpi_inflated = data.get('cpi_inflated', False)
                    if cpi_inflated:
                        index_rates = self.indexing_rates(name)
                        wage_indexed = name in ('_SS_Earnings_c',
                                                '_SS_Earnings_thd')
                        if not wage_indexed:
                            if known_years_is_int:
                                values = values[:known_years]
                            else:
                                values = values[:known_years[name]]
                    else:
                        index_rates = None
                    setattr(self, name,
                            self._expand_array(values, valtype,
                                               inflate=cpi_inflated,
                                               inflation_rates=index_rates,
                                               num_years=self._num_years))
        self.set_year(self._start_year)

    @property
    def num_years(self):
        """
        Parameters class number of parameter years property.
        """
        return self._num_years

    @property
    def current_year(self):
        """
        Parameters class current calendar year property.
        """
        return self._current_year

    @property
    def start_year(self):
        """
        Parameters class first parameter year property.
        """
        return self._start_year

    @property
    def end_year(self):
        """
        Parameters class lasst parameter year property.
        """
        return self._end_year

    def set_year(self, year):
        """
        Set parameters to their values for the specified calendar year.

        Parameters
        ----------
        year: int
            calendar year for which to set current_year and parameter values

        Raises
        ------
        ValueError:
            if year is not in [start_year, end_year] range.

        Returns
        -------
        nothing: void

        Notes
        -----
        To increment the current year, use the following statement::

            policy.set_year(policy.current_year + 1)

        where, in this example, policy is a Policy class object.
        """
        if year < self.start_year or year > self.end_year:
            msg = 'year {} passed to set_year() must be in [{},{}] range.'
            raise ValueError(msg.format(year, self.start_year, self.end_year))
        self._current_year = year
        year_zero_indexed = year - self._start_year
        if hasattr(self, '_vals'):
            for name in self._vals:
                if isinstance(name, str):
                    arr = getattr(self, name)
                    setattr(self, name[1:], arr[year_zero_indexed])

    @staticmethod
    def param_dict_for_year(cyear, param_dict, param_info):
        """
        Set parameters to their values for the specified calendar year.

        Parameters
        ----------
        cyear: int
            calendar year for which to set parameter values

        param_dict: dict
            dictionary returned by the Calculator.read_json_assumptions method

        param_info: dict
            dictionary of information about each parameter that can be used in
            param_dict, where information about each parameter must include at
            a minimum the following key-value pairs:
            'default_value': <number>
            'minimum_value': <number>
            'maximum_value': <number>

        Note
        ----
        This method may not be used by Tax-Calculator, but it is used by
        other PSL models that work with Tax-Calculator.

        Returns
        -------
        param_values_for_year: dict
            dictionary containing a key:value pair for each parameter in the
            param_info dictionary, where each pair looks like this:
            '<param_name>': <number>
        """
        assert isinstance(cyear, int)
        assert isinstance(param_dict, dict)
        assert isinstance(param_info, dict)
        # set each parameter to its default value
        pvalue = dict()
        for pname in param_info:
            pvalue[pname] = param_info[pname]['default_value']
        # update pvalue using param_dict contents
        for year in sorted(param_dict.keys()):
            assert isinstance(year, int)
            if year > cyear:
                break  # out of the for year loop
            ydict = param_dict[year]
            assert isinstance(ydict, dict)
            for pname in ydict:
                assert pname in param_info
                pval = ydict[pname]
                assert isinstance(pval, float)
                assert pval >= param_info[pname]['minimum_value']
                assert pval <= param_info[pname]['maximum_value']
                pvalue[pname] = pval
        return pvalue

    # ----- begin private methods of Parameters class -----

    def _validate_assump_parameter_names_types(self, revision):
        """
        Check validity of assumption parameter names and parameter types
        used in the specified revision dictionary.
        """
        # pylint: disable=too-many-branches,too-many-nested-blocks
        # pylint: disable=too-many-locals
        param_names = set(self._vals.keys())
        for year in sorted(revision.keys()):
            for name in revision[year]:
                if name not in param_names:
                    msg = '{} {} unknown parameter name'
                    self.parameter_errors += (
                        'ERROR: ' + msg.format(year, name) + '\n'
                    )
                else:
                    # check parameter value type avoiding use of isinstance
                    # because isinstance(True, (int,float)) is True, which
                    # makes it impossible to check float parameters
                    valtype = self._vals[name]['value_type']
                    assert isinstance(revision[year][name], list)
                    pvalue = revision[year][name][0]
                    assert not isinstance(pvalue, list)
                    pvalue = [pvalue]  # make scalar a single-item list
                    # pylint: disable=consider-using-enumerate
                    for idx in range(0, len(pvalue)):
                        pname = name
                        pval = pvalue[idx]
                        # pylint: disable=unidiomatic-typecheck
                        if valtype == 'real':
                            if type(pval) != float and type(pval) != int:
                                msg = '{} {} value {} is not a number'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
                        elif valtype == 'boolean':
                            if type(pval) != bool:
                                msg = '{} {} value {} is not boolean'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
                        elif valtype == 'integer':
                            if type(pval) != int:
                                msg = '{} {} value {} is not integer'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
                        elif valtype == 'string':
                            if type(pval) != str:
                                msg = '{} {} value {} is not a string'
                                self.parameter_errors += (
                                    'ERROR: ' +
                                    msg.format(year, pname, pval) +
                                    '\n'
                                )
        del param_names

    def _validate_assump_parameter_values(self, parameters_set):
        """
        Check values of assumption parameters in specified parameter_set.
        """
        parameters = sorted(parameters_set)
        for pname in parameters:
            pvalue = getattr(self, pname)
            for vop, vval in self._vals[pname]['valid_values'].items():
                vvalue = np.full(pvalue.shape, vval)
                assert pvalue.shape == vvalue.shape
                assert len(pvalue.shape) == 1  # parameter value is a scalar
                for idx in np.ndindex(pvalue.shape):
                    out_of_range = False
                    if vop == 'min' and pvalue[idx] < vvalue[idx]:
                        out_of_range = True
                        msg = '{} {} value {} < min value {}'
                    if vop == 'max' and pvalue[idx] > vvalue[idx]:
                        out_of_range = True
                        msg = '{} {} value {} > max value {}'
                    if out_of_range:
                        name = pname
                        self.parameter_errors += (
                            'ERROR: ' + msg.format(idx[0] + self.start_year,
                                                   name,
                                                   pvalue[idx],
                                                   vvalue[idx]) + '\n'
                        )
        del parameters

    @classmethod
    def _params_dict_from_json_file(cls):
        """
        Read DEFAULTS_FILE_NAME file and return complete dictionary.

        Parameters
        ----------
        nothing: void

        Returns
        -------
        params: dictionary
            containing complete contents of DEFAULTS_FILE_NAME file.
        """
        not_implemented = (cls.DEFAULTS_FILE_NAME is None or
                           cls.DEFAULTS_FILE_PATH is None)
        if not_implemented:
            msg = '{} and {} must be overridden by inheriting class'
            raise NotImplementedError(msg.format(
                'DEFAULTS_FILE_NAME', 'DEFAULTS_FILE_PATH'
            ))
        file_path = os.path.join(cls.DEFAULTS_FILE_PATH,
                                 cls.DEFAULTS_FILE_NAME)
        if os.path.isfile(file_path):
            with open(file_path) as pfile:
                json_text = pfile.read()
            params_dict = json_to_dict(json_text)
        else:  # find file in conda package
            params_dict = read_egg_json(
                cls.DEFAULTS_FILE_NAME)  # pragma: no cover
        return params_dict

    def _update(self, year_mods):
        """
        Private method used by public implement_reform and update_* methods
        in inheriting classes.

        Parameters
        ----------
        year_mods: dictionary containing a single YEAR:MODS pair
            see Notes below for details on dictionary structure.

        Raises
        ------
        ValueError:
            if year_mods is not a dictionary of the expected structure.

        Returns
        -------
        nothing: void

        Notes
        -----
        This is a private method that should **never** be used by clients
        of the inheriting classes.  Instead, always use the public
        implement_reform or update_consumption-like methods.
        This is a private method that helps the public methods work.

        This method implements a policy reform or consumption modification,
        the provisions of which are specified in the year_mods dictionary,
        that changes the values of some policy parameters in objects of
        inheriting classes.  This year_mods dictionary contains exactly one
        YEAR:MODS pair, where the integer YEAR key indicates the
        calendar year for which the reform provisions in the MODS
        dictionary are implemented.  The MODS dictionary contains
        PARAM:VALUE pairs in which the PARAM is a string specifying
        the policy parameter (as used in the DEFAULTS_FILE_NAME default
        parameter file) and the VALUE is a Python list of post-reform
        values for that PARAM in that YEAR.  Beginning in the year
        following the implementation of a reform provision, the
        parameter whose value has been changed by the reform continues
        to be inflation indexed, if relevant, or not be inflation indexed
        according to that parameter's cpi_inflated value loaded from
        DEFAULTS_FILE_NAME.  For a cpi-related parameter, a reform can change
        the indexing status of a parameter by including in the MODS dictionary
        a term that is a PARAM_cpi:BOOLEAN pair specifying the post-reform
        indexing status of the parameter.

        So, for example, to raise the OASDI (i.e., Old-Age, Survivors,
        and Disability Insurance) maximum taxable earnings beginning
        in 2018 to $500,000 and to continue indexing it in subsequent
        years as in current-law policy, the YEAR:MODS dictionary would
        be as follows::

            {2018: {"_SS_Earnings_c":[500000]}}

        But to raise the maximum taxable earnings in 2018 to $500,000
        without any indexing in subsequent years, the YEAR:MODS
        dictionary would be as follows::

            {2018: {"_SS_Earnings_c":[500000], "_SS_Earnings_c_cpi":False}}

        And to raise in 2019 the starting AGI for EITC phaseout for
        married filing jointly filing status (which is a two-dimensional
        policy parameter that varies by the number of children from zero
        to three or more and is inflation indexed), the YEAR:MODS dictionary
        would be as follows::

            {2019: {"_EITC_ps_MarriedJ":[[8000, 8500, 9000, 9500]]}}

        Notice the pair of double square brackets around the four values
        for 2019.  The one-dimensional parameters above require only a pair
        of single square brackets.
        """
        # pylint: disable=too-many-locals
        # check YEAR value in the single YEAR:MODS dictionary parameter
        if not isinstance(year_mods, dict):
            msg = 'year_mods is not a dictionary'
            raise ValueError(msg)
        if len(year_mods.keys()) != 1:
            msg = 'year_mods dictionary must contain a single YEAR:MODS pair'
            raise ValueError(msg)
        year = list(year_mods.keys())[0]
        if year != self.current_year:
            msg = 'YEAR={} in year_mods is not equal to current_year={}'
            raise ValueError(msg.format(year, self.current_year))
        # check that MODS is a dictionary
        if not isinstance(year_mods[year], dict):
            msg = 'mods in year_mods is not a dictionary'
            raise ValueError(msg)
        # implement reform provisions included in the single YEAR:MODS pair
        num_years_to_expand = (self.start_year + self.num_years) - year
        all_names = set(year_mods[year].keys())  # no duplicate keys in a dict
        used_names = set()  # set of used parameter names in MODS dict
        for name, values in year_mods[year].items():
            # determine indexing status of parameter with name for year
            if name.endswith('_cpi'):
                continue  # handle elsewhere in this method
            vals_indexed = self._vals[name].get('cpi_inflated', False)
            valtype = self._vals[name].get('value_type')
            name_plus_cpi = name + '_cpi'
            if name_plus_cpi in year_mods[year].keys():
                used_names.add(name_plus_cpi)
                indexed = year_mods[year].get(name_plus_cpi)
                self._vals[name]['cpi_inflated'] = indexed  # remember status
            else:
                indexed = vals_indexed
            # set post-reform values of parameter with name
            used_names.add(name)
            cval = getattr(self, name, None)
            index_rates = self._indexing_rates_for_update(name, year,
                                                          num_years_to_expand)
            nval = self._expand_array(values, valtype,
                                      inflate=indexed,
                                      inflation_rates=index_rates,
                                      num_years=num_years_to_expand)
            cval[(year - self.start_year):] = nval
        # handle unused parameter names, all of which end in _cpi, but some
        # parameter names ending in _cpi were handled above
        unused_names = all_names - used_names
        for name in unused_names:
            used_names.add(name)
            pname = name[:-4]  # root parameter name
            pindexed = year_mods[year][name]
            self._vals[pname]['cpi_inflated'] = pindexed  # remember status
            cval = getattr(self, pname, None)
            pvalues = [cval[year - self.start_year]]
            index_rates = self._indexing_rates_for_update(name, year,
                                                          num_years_to_expand)
            valtype = self._vals[pname].get('value_type')
            nval = self._expand_array(pvalues, valtype,
                                      inflate=pindexed,
                                      inflation_rates=index_rates,
                                      num_years=num_years_to_expand)
            cval[(year - self.start_year):] = nval
        # confirm that all names have been used
        assert len(used_names) == len(all_names)
        # implement updated parameters for year
        self.set_year(year)

    STRING_DTYPE = 'U9'

    # pylint: disable=invalid-name

    @staticmethod
    def _expand_array(x, x_type, inflate, inflation_rates, num_years):
        """
        Private method called only within this abstract base class.
        Dispatch to either _expand_1d or _expand_2d given dimension of x.

        Parameters
        ----------
        x : value to expand
            x must be either a scalar list or a 1D numpy array, or
            x must be either a list of scalar lists or a 2D numpy array

        x_type : string ('boolean', 'integer', 'real', 'string')

        inflate: boolean
            As we expand, inflate values if this is True, otherwise, just copy

        inflation_rates: list of inflation rates
            Annual decimal inflation rates

        num_years: int
            Number of budget years to expand

        Returns
        -------
        expanded numpy array with specified type
        """
        if not isinstance(x, list) and not isinstance(x, np.ndarray):
            msg = '_expand_array expects x to be a list or numpy array'
            raise ValueError(msg)
        if isinstance(x, list):
            if x_type == 'real':
                x = np.array(x, np.float64)
            elif x_type == 'boolean':
                x = np.array(x, np.bool_)
            elif x_type == 'integer':
                x = np.array(x, np.int8)
            elif x_type == 'string':
                x = np.array(x, np.dtype(Parameters.STRING_DTYPE))
                assert len(x.shape) == 1, \
                    'string parameters must be scalar (not vector)'
        dim = len(x.shape)
        assert dim in (1, 2)
        if dim == 1:
            return Parameters._expand_1d(x, inflate, inflation_rates,
                                         num_years)
        return Parameters._expand_2d(x, inflate, inflation_rates,
                                     num_years)

    @staticmethod
    def _expand_1d(x, inflate, inflation_rates, num_years):
        """
        Private method called only from _expand_array method.
        Expand the given data x to account for given number of budget years.
        If necessary, pad out additional years by increasing the last given
        year using the given inflation_rates list.
        """
        if not isinstance(x, np.ndarray):
            raise ValueError('_expand_1d expects x to be a numpy array')
        if len(x) >= num_years:
            return x
        string_type = x.dtype == Parameters.STRING_DTYPE
        if string_type:
            ans = np.array(['' for i in range(0, num_years)],
                           dtype=x.dtype)
        else:
            ans = np.zeros(num_years, dtype=x.dtype)
        ans[:len(x)] = x
        if string_type:
            extra = [str(x[-1]) for i in
                     range(1, num_years - len(x) + 1)]
        else:
            if inflate:
                extra = []
                cur = x[-1]
                for i in range(0, num_years - len(x)):
                    cur *= (1. + inflation_rates[i + len(x) - 1])
                    cur = round(cur, 2) if cur < 9e99 else 9e99
                    extra.append(cur)
            else:
                extra = [float(x[-1]) for i in
                         range(1, num_years - len(x) + 1)]
        ans[len(x):] = extra
        return ans

    @staticmethod
    def _expand_2d(x, inflate, inflation_rates, num_years):
        """
        Private method called only from _expand_array method.
        Expand the given data to account for the given number of budget years.
        For 2D arrays, we expand out the number of rows until we have num_years
        number of rows. For each expanded row, we inflate using the given
        inflation rates list.
        """
        if not isinstance(x, np.ndarray):
            raise ValueError('_expand_2d expects x to be a numpy array')
        if x.shape[0] >= num_years:
            return x
        ans = np.zeros((num_years, x.shape[1]), dtype=x.dtype)
        ans[:len(x), :] = x
        for i in range(x.shape[0], ans.shape[0]):
            for j in range(ans.shape[1]):
                if inflate:
                    cur = (ans[i - 1, j] *
                           (1. + inflation_rates[i - 1]))
                    cur = round(cur, 2) if cur < 9e99 else 9e99
                    ans[i, j] = cur
                else:
                    ans[i, j] = ans[i - 1, j]
        return ans

    def _indexing_rates_for_update(self, param_name,
                                   calyear, num_years_to_expand):
        """
        Private method called only in the _update method.
        """
        # pylint: disable=assignment-from-none
        wage_indexed = param_name in ('_SS_Earnings_c', '_SS_Earnings_thd')
        if wage_indexed:
            rates = self.wage_growth_rates()
        else:
            rates = self.inflation_rates()
        if rates:
            expanded_rates = [rates[(calyear - self.start_year) + i]
                              for i in range(0, num_years_to_expand)]
            return expanded_rates
        return None
