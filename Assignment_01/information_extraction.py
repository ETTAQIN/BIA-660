from __future__ import print_function
import re
import spacy

from pyclausie import ClausIE


nlp = spacy.load('en')
re_spaces = re.compile(r'\s+')


class Person(object):
    def __init__(self, name, likes=None, dislikes=None, has=None, travels=None):
        """
        :param name: the person's name
        :type name: basestring
        :param likes: (Optional) an initial list of likes
        :type likes: list
        :param dislikes: (Optional) an initial list of likes
        :type dislikes: list
        :param has: (Optional) an initial list of things the person has
        :type has: list
        :param travels: (Optional) an initial list of the person's travels
        :type travels: list
        """
        self.name = name
        self.likes = [] if likes is None else likes
        self.dislikes = [] if dislikes is None else dislikes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels

    def __repr__(self):
        return self.name


class Pet(object):
    def __init__(self, pet_type, name=None):
        self.name = name
        self.type = pet_type


class Trip(object):
    def __init__(self, departs_to, departs_on=None):
        self.departs_to = departs_to
        self.departs_on = departs_on


persons = []
pets = []
trips = []


def get_data_from_file(file_path='./assignment_01.data'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if not line.startswith(('$$$', '###', '==='))]

    return cleaned_lines


def select_person(name):
    for person in persons:
        if person.name == name:
            return person


def add_person(name):
    person = select_person(name)

    if person is None:
        new_person = Person(name)
        persons.append(new_person)

        return new_person

    return person


def select_pet(name):
    for pet in pets:
        if pet.name == name:
            return pet


def add_pet(type, name=None):
    pet = None

    if name:
        pet = select_pet(name)

    if pet is None:
        pet = Pet(type, name)
        pets.append(pet)

    return pet


def select_trip(departs_to, departs_on):
    for trip in trips:
        if trip.departs_to == departs_to and trip.departs_on == departs_on:
            return trip


def add_trip(departs_to, departs_on):
    trip = None

    if departs_to and departs_on:
        trip = select_trip(departs_to, departs_on)

    if trip is None:
        trip = Trip(departs_to, departs_on)
        trips.append(trip)

    return trip


def get_persons_pet(person_name):

    person = select_person(person_name)

    for thing in person.has:
        if isinstance(thing, Pet):
            return thing


def process_relation_triplet(triplet):
    """
    Process a relation triplet found by ClausIE and store the data
    find relations of types:
    (PERSON, likes, PERSON)
    (PERSON, dislikes, PERSON)
    (PERSON, has, PET)
    (PET, has_name, NAME)
    (PERSON, travels, TRIP)
    (TRIP, departs_on, DATE)
    (TRIP, departs_to, PLACE)
    :param triplet: The relation triplet from ClausIE
    :type triplet: tuple
    :return: a triplet in the formats specified above
    :rtype: tuple
    """

    sentence = triplet.subject + ' ' + triplet.predicate + ' ' + triplet.object

    doc = nlp(unicode(sentence))

    for t in doc:
        if t.pos_ == 'VERB' and t.head == t:
            root = t
            break
        elif t.pos_ == 'NOUN' and t.head == t:
            root = t
            break
    # also, if only one sentence
    # root = doc[:].root

    """
    CURRENT ASSUMPTIONS:
    - People's names are unique (i.e. there only exists one person with a certain name).
    - Pet's names are unique
    - The only pets are dogs and cats
    - Only one person can own a specific pet
    - A person can own only one pet
    """
    '''test for root.lemma_
    if root.lemma_ != 'like' and root.lemma_ != 'be' and root.lemma_ != 'have' and root.lemma_ != 'name':
        print(root.lemma_, end=' <- ')
        print(root.text)
    '''
    # Process (PERSON, likes, PERSON) relations
    if root.lemma_ == 'like' and root.text != 'like':
        if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG'] and triplet.object in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG']:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            if o not in s.likes:  # eliminate duplicate names
                s.likes.append(o)

    # Process (PERSON and PERSON, are, friends) relations
    if root.lemma_ == 'be':
        if triplet.object == 'friends':
            temp1 = triplet.subject.split(' ')
            temp2 = []
            for a in temp1:
                if a in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG']:
                    s = add_person(a)
                    temp2.append(s)
            for b in temp2:
                for c in temp2:
                    if b is not c:
                        if b not in c.likes:  # eliminate duplicate names
                            c.likes.append(b)
                        if c not in b.likes:
                            b.likes.append(c)

    if root.lemma_ == 'be' and triplet.object.startswith('friends with'):
        fw_doc = nlp(unicode(triplet.object))
        with_token = [t for t in fw_doc if t.text == 'with'][0]
        fw_who = [t for t in with_token.children if t.dep_ == 'pobj'][0].text
        # fw_who = [e for e in fw_doc.ents if e.label_ == 'PERSON'][0].text
        if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG'] and fw_who in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG']:
            s = add_person(triplet.subject)
            o = add_person(fw_who)
            if o not in s.likes:  # eliminate duplicate names
                s.likes.append(o)
            if s not in o.likes:  # eliminate duplicate names
                o.likes.append(s)

    # Process (PERSON, dislikes, PERSON) relations
    if root.lemma_ == 'like':
        if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG'] and triplet.object in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.label_ == 'ORG']:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            s.dislikes.append(o)

    # Process (PERSON, has, PET) relations
    if root.lemma_ == 'have':
        if ('dog' in triplet.object or 'cat' in triplet.object) and triplet.object.find('named') == -1:
            # without pet.name
            s = add_person(triplet.subject)
            if 'dog' in triplet.object:
                o = add_pet('dog')
            else:
                o = add_pet('cat')
            if s.has == []:
                s.has.append(o)
        elif 'dog' in triplet.object or 'cat' in triplet.object:
            # with pet.name
            s = add_person(triplet.subject)
            pet_name = triplet.object[triplet.object.find('named')+6:]
            if 'dog' in triplet.object:
                o = add_pet('dog', pet_name)
            else:
                o = add_pet('cat', pet_name)
            if s.has == []:
                s.has.append(o)

    # Process (PET, has, NAME)
    if triplet.subject.endswith('name') and ('dog' in triplet.subject or 'cat' in triplet.subject):
        obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
        # handle single names, but what about compound names? Noun chunks might help.
        if obj_span[0].pos_ == 'PROPN':
            name = triplet.object
            subj_start = sentence.find(triplet.subject)
            subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

            s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON' or token.ent_type_ == 'ORG']
            assert len(s_people) == 1
            s_person = select_person(s_people[0])

            s_pet_type = 'dog' if 'dog' in triplet.subject else 'cat'

            if s_person.has != []:
                s_person.has[0].name = name
            else:
                pet = add_pet(s_pet_type, name)
                s_person.has.append(pet)

    # Process (PERSON, go, SOMEWHERE/SOMETIME)
    if root.lemma_ == 'take' or root.lemma_ == 'fly' or root.lemma_ == 'go' or root.lemma_ == 'leave':
        trip = None
        for b in [e.text for e in doc.ents if e.label_ == 'GPE']:
            for c in [d.text for d in doc.ents if d.label_ == 'DATE']:
                trip = add_trip(b, c)
        for a in [f.text for f in doc.ents if f.label_ == 'PERSON' or f.label_ == 'ORG']:
            a = add_person(a)
            a.travels.append(trip)


def preprocess_question(question):
    # remove articles: a, an, the

    q_words = question.split(' ')

    # when won't this work?
    for article in ('a', 'an', 'the'):
        try:
            q_words.remove(article)
        except:
            pass

    return re.sub(re_spaces, ' ', ' '.join(q_words))


def has_question_word(string):
    # note: there are other question words
    for qword in ('who', 'what', 'when'):
        if qword in string.lower():
            return True

    return False


def process_data_from_input_file():
    sents = get_data_from_file()
    cl = ClausIE.get_instance()
    triples = cl.extract_triples(sents)
    for t in triples:
        # print(t)
        process_relation_triplet(t)


def answer_question(question_string):
    answers = []
    cl = ClausIE.get_instance()
    try:
        q_trip = cl.extract_triples([preprocess_question(question_string)])[0]
        sentence = q_trip.subject + ' ' + q_trip.predicate + ' ' + q_trip.object
        doc = nlp(unicode(sentence))

        for t in doc:
            if t.pos_ == 'VERB' and t.head == t:
                root = t

        #print(q_trip)
        #print(root.lemma_)
        # (WHO, has, PET)
        if q_trip.subject.lower() == 'who' and q_trip.object == 'dog' or q_trip.object == 'cat':
            answer = '{} has a {} named {}.'

            for person in persons:
                pet = get_persons_pet(person.name)
                if q_trip.object == 'dog' and pet and pet.type == 'dog':
                    answers.append(answer.format(person.name, 'dog', pet.name))
                elif q_trip.object == 'cat' and pet and pet.type == 'cat':
                    answers.append(answer.format(person.name, 'cat', pet.name))
        for answer in answers:
            print (answer)

        # (Who, go, SOMEWHERE)
        if q_trip.subject.lower() == 'who' and (root.lemma_ == 'take' or root.lemma_ == 'fly' or root.lemma_ == 'go' or root.lemma_ == 'leave'):
            answer = '{} goes to {}.'
            for a in [e.text for e in doc.ents if e.label_ == 'GPE']:
                for person in persons:
                    for b in person.travels:
                        if b != None:
                            if b.departs_to == a:
                                answers.append(answer.format(person.name, a))
            if answers == []:
                print("No one is going to", a)
            else:
                for answer in answers:
                    print(answer)

        # (Does, PERSON, like, PERSON)
        if not has_question_word(question_string):
            temp = q_trip.subject.split(' ')
            flag = False
            for a in temp:
                if a in [e.text for e in doc.ents if e.label_ == 'PERSON']:
                    try:
                        select_person(a).likes
                    except AttributeError:
                        print(q_trip.object, "is not a person in the database.")
                        break
                    if select_person(q_trip.object) in select_person(a).likes:
                        print("Yes.")
                        flag = True
                    if flag == False:
                        print("No.")

        # (When is <person> [going to|flying to|traveling to] <place>)
        if q_trip.object.lower().endswith('when'):
            flag = False
            a = select_person(q_trip.subject)
            if a != None:
                for b in a.travels:
                    for c in [e.text for e in doc.ents if e.label_ == 'GPE']:
                        if b != None:
                            if b.departs_to == c:
                                print(b.departs_on)
                                flag = True
                        else:
                            print(q_trip.subject, "is not going to anywhere.")
            else:
                print(q_trip.subject, "is not in the database. Try another person name.")
                flag = True
            try:
                c
            except NameError:
                print("It is not even a place!!")
                flag = True
            if flag == False:
                print(q_trip.subject,"is not going to", c)

        # (Who likes <person>?)
        if q_trip.subject.lower() == 'who' and root.lemma_ == 'like':
            answer = '{} like(s) {}.'
            people = []
            temp = ''
            for person in persons:
                for like in person.likes:
                    if like.name == q_trip.object:
                        people.append(person)
            for a in people:
                temp += a.name
                temp += ', '
            temp = temp[:-2]
            if temp == '':
                print(answer.format('No one',q_trip.object))
            else:
                print(answer.format(temp,q_trip.object))

        # (Who does <person> like?)
        if q_trip.object.lower() == 'who':
            answer = '{} likes {}.'
            temp = ''
            try:
                for a in select_person(q_trip.subject).likes:
                    temp += a.name
                    temp += ', '
                temp = temp[:-2]
                print(answer.format(q_trip.subject, temp))
            except AttributeError:
                print(q_trip.subject, "is not a person in the database.")
    except ValueError:
        answer = 'The name of {}\'s {} is {}.'
        ques = question_string.split(' ')
        petType = ques[-1][:-1]
        personName = ques[-2][:-2]
        try:
            for a in select_person(personName).has:
                if a.type == petType:
                    print(answer.format(personName, petType, a.name))
        except AttributeError:
            print(personName, "is not a person in the database.")

def main():
    process_data_from_input_file()
    question = ' '
    flag = True
    while(flag == True):
        while question[-1] != '?':
            question = raw_input("Please enter your question: ")

            if question[-1] != '?':
                print('This is not a question... please try again')

        answer_question(question)
        ques = raw_input("More question?(Y/N) ")
        if ques.lower() == 'n':
            flag=False
        question = ' '


if __name__ == '__main__':
    main()