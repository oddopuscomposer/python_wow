from sqlalchemy import Column, Integer

from database.main import Base


class LootTable(Base):
    __tablename__ = 'loot_table'

    entry = Column(Integer, primary_key=True)
    item1_id = Column(Integer)
    item1_chance = Column(Integer)
    item2_id = Column(Integer)
    item2_chance = Column(Integer)
    item3_id = Column(Integer)
    item3_chance = Column(Integer)
    item4_id = Column(Integer)
    item4_chance = Column(Integer)
    item5_id = Column(Integer)
    item5_chance = Column(Integer)
    item6_id = Column(Integer)
    item6_chance = Column(Integer)
    item7_id = Column(Integer)
    item7_chance = Column(Integer)
    item8_id = Column(Integer)
    item8_chance = Column(Integer)
    item9_id = Column(Integer)
    item9_chance = Column(Integer)
    item10_id = Column(Integer)
    item10_chance = Column(Integer)
    item11_id = Column(Integer)
    item11_chance = Column(Integer)
    item12_id = Column(Integer)
    item12_chance = Column(Integer)
    item13_id = Column(Integer)
    item13_chance = Column(Integer)
    item14_id = Column(Integer)
    item14_chance = Column(Integer)
    item15_id = Column(Integer)
    item15_chance = Column(Integer)
    item16_id = Column(Integer)
    item16_chance = Column(Integer)
    item17_id = Column(Integer)
    item17_chance = Column(Integer)
    item18_id = Column(Integer)
    item18_chance = Column(Integer)
    item19_id = Column(Integer)
    item19_chance = Column(Integer)
    item20_id = Column(Integer)
    item20_chance = Column(Integer)
