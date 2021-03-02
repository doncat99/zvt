from zvt.api.data_type import Region, Provider
from zvt.api.quote import get_kdata
from zvt.contract import IntervalLevel
from zvt.contract.api import get_db_session
from ..context import init_test_context

init_test_context()

day_k_session = get_db_session(region=Region.CHN,
                               provider=Provider.JoinQuant,
                               db_name='stock_1d_kdata')

day_1h_session = get_db_session(region=Region.CHN,
                                provider=Provider.JoinQuant,
                                db_name='stock_1h_kdata')


def test_jq_603220_kdata():
    df = get_kdata(region=Region.CHN, entity_id='stock_sh_603220',
                   session=day_k_session, level=IntervalLevel.LEVEL_1DAY,
                   provider=Provider.JoinQuant)
    print(df)
    df = get_kdata(region=Region.CHN, entity_id='stock_sh_603220',
                   session=day_1h_session, level=IntervalLevel.LEVEL_1HOUR,
                   provider=Provider.JoinQuant)
    print(df)
