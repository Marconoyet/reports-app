from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    @declared_attr
    def __table_args__(cls):
        return {'schema': 'u704613426_reports'}
