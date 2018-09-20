import pandas as pd
from pytesmo.validation_framework.data_manager import DataManager
from datetime import datetime
from pytz import UTC
import pytest

class FaultyReader(object):
    '''
    Reader class to test warnings and exceptions happening in data manager when
    read_ts returns edge cases or non-valid data.
    '''
    def read_ts(self, gpi):
        if gpi == 0:
            raise IOError("Couldn't read file because of waxing moon!")
        elif gpi == 1:
            raise RuntimeError("No such file or directory")
        elif gpi == 2:
            return None
        elif gpi == 3:
            return []
        elif gpi == 4:
            return "Foobar"
        elif gpi == 5:
            return pd.DataFrame()
        elif gpi == 6:
            idx = pd.date_range(start='2018-01-01', periods=8, freq='D')
            return pd.DataFrame(index=idx, data=range(8))
        elif gpi == 7:
            raise RuntimeError("I'm too lazy...")
        else:
            return None


def setup_TestDataManager():

    ds1 = FaultyReader()
    ds2 = FaultyReader()

    datasets = {
        'DS1': {
            'class': ds1,
            'columns': ['soil moisture'],
            'args': [],
            'kwargs': {}
        },
        'DS2': {
            'class': ds2,
            'columns': ['sm'],
            'args': [],
            'kwargs': {},
            'grids_compatible': True
        },
    }

    period = [datetime(1978, 1, 1, tzinfo=UTC), datetime(1998, 1, 1, tzinfo=UTC)]
    dm = DataManager(datasets, 'DS1', period=period)
    return dm

def test_data_manager_warnings():
    dm = setup_TestDataManager()

    # the gpis 0 through 6 should produce various different warnings from the
    # data manager
    for i in range(7):
        print("Testing warnings, iteration {}".format(i))
        with pytest.warns(UserWarning):
            dm.read_reference(i)
        with pytest.warns(UserWarning):
            dm.read_other('DS2', i)

    # gpi 7 should raise a runtime error
    with pytest.raises(RuntimeError):
        dm.read_reference(7)
    with pytest.raises(RuntimeError):
        dm.read_other('DS2', 7)
