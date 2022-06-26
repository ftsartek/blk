from io import StringIO
from textwrap import dedent
import pytest


@pytest.fixture(scope='session')
def json_mixed_dict_section_json_2():
    json = """\
    {
      "bool": [
        true
      ],
      "str": [
        "hello"
      ],
      "int": [
        0,
        1
      ],
      "long": [
        2
      ],
      "float": [
        3.0
      ],
      "int2": [
        [1,2]
      ],
      "int3": [
        [1,2,3]
      ],
      "color": [
        "#01020304"
      ],
      "float2": [
        [1.0,2.0]
      ],
      "float3": [
        [1.0,2.0,3.0]
      ],
      "float4": [
        [1.0,2.0,3.0,4.0]
      ],
      "float12": [
        [
          [1.0,2.0,3.0],
          [4.0,5.0,6.0],
          [7.0,8.0,9.0],
          [10.0,11.0,12.0]
        ]
      ],
      "inner": [
        {
          "a": [
            1
          ],
          "b": [
            2
          ]
        }
      ]
    }"""
    return dedent(json)


@pytest.fixture(scope='session')
def json_dict_sections_only_dict_section_json_2():
    json = """\
    {
      "alpha": [
        []
      ],
      "beta": [
        []
      ]
    }"""
    return dedent(json)


@pytest.fixture(scope='session')
def json_dict_section_with_same_id_sub_json_2():
    json = """\
    {
      "sub1": [
        {
          "scalar": [
            42
          ]
        }
      ],
      "sub2": [
        {
          "scalar": [
            42
          ]
        }
      ]
    }"""
    return dedent(json)


@pytest.fixture(scope='session')
def json_dict_section_with_same_id_sub_deep_json_2():
    json = """\
    {
      "inter1": [
        {
          "sub": [
            {
              "scalar": [
                42
              ]
            }
          ]
        }
      ],
      "inter2": [
        {
          "sub": [
            {
              "scalar": [
                42
              ]
            }
          ]
        }
      ]
    }"""
    return dedent(json)


@pytest.fixture()
def ostream():
    return StringIO()
