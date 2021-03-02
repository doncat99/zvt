# -*- coding: utf-8 -*-
from zvt.api.data_type import Region, Provider, EntityType
from zvt.contract.api import get_entities
from ..context import init_test_context

init_test_context()


def test_basic_get_securities():
    items = get_entities(region=Region.CHN, entity_type=EntityType.Stock, provider=Provider.EastMoney)
    print(items)
    items = get_entities(region=Region.CHN, entity_type=EntityType.Index, provider=Provider.EastMoney)
    print(items)