import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()


class Seen_persones(Base):
    __tablename__ = 'seen_persones'

    id = sq.Column(sq.Integer, primary_key=True)
    seen_person_id = sq.Column(sq.Integer, sq.ForeignKey("person.person_id"))
    user_id_user = sq.Column(sq.Integer, sq.ForeignKey("user.user_id"))
    liked = sq.Column(sq.Boolean, default=False)


class User(Base):
    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=20))
    bdate = sq.Column(sq.String)
    sex = sq.Column(sq.Integer)
    city = sq.Column(sq.Integer)
    age = sq.Column(sq.Integer)
    person = relationship(Seen_persones, backref='user')



    def __str__(self):
        return f"{self.user_id}, {self.first_name}, {self.bdate}, {self.city}, {self.city}"


class Person(Base):
    __tablename__ = 'person'

    person_id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=20))
    bdate = sq.Column(sq.String)
    sex = sq.Column(sq.Integer)
    city = sq.Column(sq.Integer)
    user = relationship(Seen_persones, backref="person")

    def __str__(self):
        return f"{self.person_id}, {self.name}, {self.bdate}, {self.sex}, {self.city}"



def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


DSN = "postgresql://postgres:123@localhost:5432/VKinder"
engine = sq.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()
# session.commit()
# q = session.query(Person).filter(Person.person_id == 1, Person.city == 1).all()
# q = session.query(Seen_persones).filter(Seen_persones.seen_person_id == 123, Seen_persones.user_id_user == 456).all()
# for i in q:
#     print(i)
# print(bool(q))
# person = Seen_persones(seen_person_id = 555686640, user_id_user = 7889219, liked = False)
# session.add(person)
# session.commit()

session.close()
