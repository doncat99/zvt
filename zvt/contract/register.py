# -*- coding: utf-8 -*-
import logging
from typing import List, Dict

import sqlalchemy
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.engine.reflection import Inspector

from zvt import zvt_config
from zvt.api.data_type import Region, Provider, EntityType
from zvt.contract import EntityMixin, zvt_context, Mixin
from zvt.database.api import get_db_engine, get_db_session_factory, set_db_name
from zvt.utils.utils import add_to_map_list

logger = logging.getLogger(__name__)

# db_name -> [declarative_meta1,declarative_meta2...]
dbname_map_schemas = {}

# provider -> [db_name1,db_name2...]
provider_map_dbnames = {}

# all registered entity types
entity_types = []

# db_name -> [declarative_meta1,declarative_meta2...]
dbname_map_index = {}


def register_entity(entity_type: EntityType = None):
    def register(cls):
        # register the entity
        if issubclass(cls, EntityMixin):
            entity_type_ = entity_type
            if not entity_type:
                entity_type_ = EntityType(cls.__name__.lower())

            if entity_type_ not in entity_types:
                entity_types.append(entity_type_)
            zvt_context.entity_schema_map[entity_type_] = cls
        return cls
    return register


def register_schema(regions: List[Region],
                    providers: Dict[(Region, List[Provider])],
                    db_name: str,
                    schema_base: DeclarativeMeta,
                    entity_type: EntityType = None):
    """
    function for register schema,please declare them before register

    :param providers: the supported providers for the schema
    :type providers:
    :param db_name: database name for the schema
    :type db_name:
    :param schema_base:
    :type schema_base:
    :param entity_type: the schema related entity_type
    :type entity_type:
    :return:
    :rtype:
    """
    schemas = []
    for region in regions:
        for item in schema_base._decl_class_registry.items():
            cls = item[1]
            if type(cls) == DeclarativeMeta:
                # register provider to the schema
                [cls.register_provider(region, provider) for provider in providers[region] if issubclass(cls, Mixin)]

                if dbname_map_schemas.get(db_name):
                    schemas = dbname_map_schemas[db_name]
                zvt_context.schemas.append(cls)

                if entity_type:
                    add_to_map_list(the_map=zvt_context.entity_map_schemas, key=entity_type, value=cls)
                schemas.append(cls)

        # create the db & table
        engine = get_db_engine(region, schema_base, db_name=db_name)
        if engine is None:
            continue

        for provider in providers[region]:
            # track in in  _providers
            if region in zvt_context.providers.keys():
                if provider not in zvt_context.providers[region]:
                    zvt_context.providers[region].append(provider)
            else:
                zvt_context.providers.update({region: [provider]})

            if not provider_map_dbnames.get(provider):
                provider_map_dbnames[provider] = []
            provider_map_dbnames[provider].append(db_name)

            session_fac = get_db_session_factory(region, provider, db_name=db_name)
            session_fac.configure(bind=engine)

        set_db_name(db_name, schema_base)
        inspector = Inspector.from_engine(engine)

        if not dbname_map_index.get(region):
            dbname_map_index[region] = []

        # create index for 'id', 'timestamp', 'entity_id', 'code', 'report_period', 'updated_timestamp
        for table_name, table in iter(schema_base.metadata.tables.items()):
            if table_name in dbname_map_index[region]:
                continue

            dbname_map_index[region].append(table_name)

            index_column_names = [index['name'] for index in inspector.get_indexes(table_name)]

            if zvt_config['debug'] == 2:
                logger.debug(f'create index -> engine: {engine}, table: {table_name}, index: {index_column_names}')

            for col in ['timestamp', 'entity_id', 'code', 'report_period', 'created_timestamp', 'updated_timestamp']:
                if col in table.c:
                    index_name = '{}_{}_index'.format(table_name, col)
                    if index_name not in index_column_names:
                        column = eval('table.c.{}'.format(col))
                        if col == 'timestamp':
                            column = eval('table.c.{}.desc()'.format(col))
                        else:
                            column = eval('table.c.{}'.format(col))
                        # index = sqlalchemy.schema.Index(index_name, column, unique=(col=='id'))
                        index = sqlalchemy.schema.Index(index_name, column)
                        index.create(engine)

            for cols in [('timestamp', 'entity_id'), ('timestamp', 'code')]:
                if (cols[0] in table.c) and (col[1] in table.c):
                    index_name = f'{table_name}_{col[0]}_{col[1]}_index'
                    if index_name not in index_column_names:
                        column0 = eval('table.c.{}'.format(col[0]))
                        column1 = eval('table.c.{}'.format(col[1]))
                        index = sqlalchemy.schema.Index(index_name, column0, column1)
                        index.create(engine)

    dbname_map_schemas[db_name] = schemas
