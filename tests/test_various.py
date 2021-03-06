import uuid
from typing import Optional, NewType
from unittest import TestCase

import jsons
from tests.test_specific_versions import only_version_3


class C:
    def __init__(self, x: 'str'):
        self.x = x


class Node:
    def __init__(self, value: int, next: Optional['Node'] = None):
        self.value = value
        self.next = next


class TestVarious(TestCase):
    def test_load_obj_with_str_hint(self):
        loaded = jsons.load({'x': 'test'}, C)
        self.assertEqual('test', loaded.x)

    def test_load_obj_with_str_cls(self):
        loaded = jsons.load({'x': 'test'}, 'tests.test_various.C')
        self.assertEqual('test', loaded.x)

    def test_dump_recursive_structure(self):
        linkedlist = Node(10, Node(20, Node(30)))
        dumped = jsons.dump(linkedlist)
        expected = {
            'value': 10,
            'next': {
                'value': 20,
                'next': {
                    'value': 30,
                    'next': None
                }
            }
        }
        self.assertDictEqual(expected, dumped)

    def test_load_recursive_structure(self):
        source = {
            'value': 10,
            'next': {
                'value': 20,
                'next': {
                    'value': 30,
                    'next': None
                }
            }
        }
        loaded = jsons.load(source, Node)
        self.assertEqual(30, loaded.next.next.value)

    def test_dump_load_newtype(self):
        Uid = NewType('uid', str)

        class User:
            def __init__(self, uid: Uid, name: str):
                self.uid = uid
                self.name = name

        dumped = jsons.dump(User('uid', 'name'))
        loaded = jsons.load(dumped, User)

        self.assertEqual('uid', loaded.uid)
        self.assertEqual('name', loaded.name)

    @only_version_3(6, and_above=True)
    def test_custom_uuid_serialization(self):
        from version_with_dataclasses import User
        user = User(uuid.uuid4(), 'name')

        def custom_uuid_serializer(obj, **kwargs):
            return str(obj)

        def custom_uuid_deserializer(obj, cls, **kwargs):
            return cls(obj)

        jsons.set_serializer(custom_uuid_serializer, uuid.UUID)
        jsons.set_deserializer(custom_uuid_deserializer, uuid.UUID)

        dumped = jsons.dump(user)
        self.assertEqual(dumped['user_id'], str(user.user_id))

        loaded = jsons.load(dumped, User)
        self.assertEqual(user.user_id, loaded.user_id)

        self.assertEqual('name', loaded.name)
