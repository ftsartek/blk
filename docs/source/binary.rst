==================
Двоичные файлы BLK
==================

В качестве примеров закодирована секция:

.. code-block:: javascript

    "vec4f":p4 = 1.25, 2.5, 5, 10
        "int":i = 42
        "long":i64 = 0x40
        "alpha" {
          "str":t = "hello"
          "bool":b = true
          "color":c = 0x1, 0x2, 0x3, 0x4
          "gamma" {
            "vec2i":ip2 = 3, 4
            "vec2f":p2 = 1.25, 2.5
            "transform":m = [[1, 0, 0] [0, 1, 0] [0, 0, 1] [1.25, 2.5, 5]]
          }
        }
        "beta" {
          "float":r = 1.25
          "vec2i":ip2 = 1, 2
          "vec3f":p3 = 1.25, 2.5, 5
        }

---------------
Общие структуры
---------------

.. list-table:: Тип файла по первому байту
    :header-rows: 1
    :align: left

    * - Первый октет
      - Тип
    * - 0x00
      - BBF
    * - 0x01
      - FAT
    * - 0x02
      - FAT_ZST
    * - 0x03
      - SLIM
    * - 0x04
      - SLIM_ZST
    * - 0x05
      - SLIM_ZST_DICT

.. list-table:: Таблица параметров
    :header-rows: 1
    :align: left

    * - Псевдоним
      - Код типа
      - Конструктор
      - Длина, октетов
      - Короткий
    * - Str
      - 0x01
      - CString
      - Var
      - \
    * - Int
      - 0x02
      - Int32sl
      - 4
      - 🗸
    * - Float
      - 0x03
      - Float32sl
      - 4
      - 🗸
    * - Float2
      - 0x04
      - Float32sl[2]
      - 8
      - \
    * - Float3
      - 0x05
      - Float32sl[3]
      - 12
      - \
    * - Float4
      - 0x06
      - Float32sl[4]
      - 16
      - \
    * - Int2
      - 0x07
      - Int32sl[2]
      - 8
      - \
    * - Int3
      - 0x08
      - Int32sl[3]
      - 12
      - \
    * - Bool
      - 0x09
      - Int32ul
      - 4
      - 🗸
    * - Color
      - 0x0a
      - Int8ul[4]
      - 4
      - 🗸
    * - Float12
      - 0x0b
      - Float32sl[12]
      - 48
      - \
    * - Long
      - 0x0c
      - Int64sl
      - 8
      - \

Целое переменной длины
======================

Формат ULEB128 ``vlq_base128_le``

Тегированный индекс (Tagged index)
==================================

Тегированный индекс кодирует вид контейнера строк и адрес строки в этом контейнере. Порядок байтов LE.

.. drawio-image:: diagrams/tagged_index.drawio

Tag
    Bit(1), тег. Строка выбирается из карты имен, если тег 1, иначе из блока данных длинных параметров.

Index
    Bit(31), индекс. Индекс в карте имен или смещение в блоке длинных параметров.

Структура ParameterInfo
=======================

Структура параметра кодирует именованный параметр.

.. drawio-image:: diagrams/parameter_info.drawio

Name ID
    Int24ul, индекс имени в карте имен.

Type ID
    Int8ul, код типа параметра.

Parameter data
    | Int32ul, индекс длинного параметра для кодов типа ``Str``, ``Float12``, ``Float4``, ``Float3``, ``Float2``, ``Int3``, ``Int2``, ``Long``.
    | Тегированный индекс для кода типа ``Str``.
    | Значение коротких параметров для кодов типа ``Color``, ``Int``, ``Float``, ``Bool``.

Структура BlockInfo
===================

Структура блока кодирует блок, именованный или безымянный.

.. drawio-image:: diagrams/block_info.drawio

Name ID
    VarInt, идентификатор имени блока.
    | Если значение t больше нуля, соответствует значению (t - 1) из карты имен.
    | Специальное значение t = 0 для корневого блока, который не имеет имени.

Parameters count
    VarInt, число параметров, выбираемых из потока параметров.

Blocks count
    VarInt, число подблоков.

First block index
    (VarInt)?, индекс первого подблока, если есть.

-------------
Файл типа FAT
-------------

Автономный файл.

Примеры:

* ``WarThunder/game.vromfs.bin/danetlibs/route_prober/templates/route_prober.blk``
* ``tests/samples/section_fat.blk``

.. drawio-image:: diagrams/fat.drawio

File type
    Int8ul, тип файла FileType.FAT.

Names count
    VarInt, количество имен.

Names data size
    VarInt, размер массива имен в октетах, если names count > 0.

Names[Names count]
    | Массив CString имен, если names count > 0.
    | Идентификаторы имен по порядку чтения массива.

Blocks count
    VarInt, количество блоков в файле, включая корневой блок.

Parameters count
    VarInt, количество параметров в файле.

Parameters data size
    VarInt, размер массива длинных параметров в октетах, если есть длинные параметры.

Parameters data
    | Регион длинных параметров, если есть длинные параметры.
    | Смещение в структуре ParameterInfo от начала региона.

ParameterInfo[Parameters count]
    | Массив структур ParameterInfo, если parameters count > 0.
    | Идентификаторы параметров по порядку чтения массива.

BlockInfo[Block count]
    | Массив структур BlockInfo, включая корневой блок, если blocks count > 0.
    | Идентификаторы блоков по порядку чтения массива.
    | Блоки перечислены при обходе дерева блоков в ширину.

Пример разбора
==============

Файл tests/samples/section_fat.blk
----------------------------------

.. drawio-image:: diagrams/section_fat_dump.drawio

Карта имен
----------

.. list-table:: Карта имен и строк
    :header-rows: 1
    :align: left

    * - Индекс
      - Имя
    * - 0x00
      - \'vec4f\'
    * - 0x01
      - \'int\'
    * - 0x02
      - \'long\'
    * - 0x03
      - \'alpha\'
    * - 0x04
      - \'str\'
    * - 0x05
      - \'bool\'
    * - 0x06
      - \'color\'
    * - 0x07
      - \'gamma\'
    * - 0x08
      - \'vec2i\'
    * - 0x09
      - \'vec2f\'
    * - 0x0a
      - \'transform\'
    * - 0x0b
      - \'beta\'
    * - 0x0c
      - \'float\'
    * - 0x0d
      - \'vec3f\'

Массив структур ParameterInfo и регион Parameters data
------------------------------------------------------

.. drawio-image:: diagrams/section_fat_param_info_array_and_params_data_dump.drawio

.. list-table:: Карта параметров
    :header-rows: 1
    :align: left
    :widths: 10 20 70

    * - Индекс
      - Имя
      - Значение
    * - 0
      - \'vec4f\'
      - Float4(1.25, 2.5, 5.0, 10.0)
    * - 1
      - \'int\'
      - Int(42)
    * - 2
      - \'long\'
      - Long(64)
    * - 3
      - \'str\'
      - Str(\'hello\')
    * - 4
      - \'bool\'
      - true
    * - 5
      - \'color\'
      - Color(1, 2, 3, 4)
    * - 6
      - \'float\'
      - Float(1.25)
    * - 7
      - \'vec2i\'
      - Int2(1, 2)
    * - 8
      - \'vec3f\'
      - Float3(1.25, 2.5, 5.0)
    * - 9
      - \'vec2i\'
      - Int2(3, 4)
    * - 10
      - \'vec2f\'
      - Float2(1.25, 2.5)
    * - 11
      - \'transform\'
      - Float12(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.25, 2.5, 5.0)

Массив структур BlockInfo
-------------------------

.. drawio-image:: diagrams/section_fat_block_info_array_dump.drawio

.. list-table:: Карта блоков
    :header-rows: 1
    :align: left
    :widths: 10 20 35 35

    * - Индекс
      - Имя
      - Индексы параметров
      - Индексы подблоков
    * - 0
      - None
      - (0, 1, 2)
      - (1, 2)
    * - 1
      - \'alpha\'
      - (3, 4, 5)
      - (3, )
    * - 2
      - \'beta\'
      - (6, 7, 8)
      - ()
    * - 3
      - \'gamma\'
      - (9, 10, 11)
      - ()

Дерево блоков
^^^^^^^^^^^^^

.. drawio-image:: diagrams/section_fat_blocks_tree.drawio

-----------------
Файл типа FAT_ZST
-----------------

Сжатый автономный файл, сжатый по алгоритму zstandard.

Примеры:

* ``WarThunder/cache/binary.2.17.0/regional.vromfs.bin/dldata/downloadable_decals.blk``
* ``tests/samples/section_fat_zst.blk``

.. drawio-image:: diagrams/fat_zst.drawio

File type
    Int8ul, тип файла FileType.FAT_ZST.

Zstd stream size
    Int24ul, размер zstd потока октетах.

Zstd stream
    Сжатый по алгоритму zstandard файл типа FAT.

Пример разбора
==============

Файл tests/samples/section_fat_zst.blk
--------------------------------------

.. drawio-image:: diagrams/section_fat_zst_dump.drawio

-------
Файл NM
-------

Разделяемый файл имен.

Примеры:

* ``WarThunder/aces.vromfs.bin/nm``
* ``tests/samples/nm``

.. drawio-image:: diagrams/nm.drawio

Names digest
    | Bit(64), дайджест карты имен.
    | Алгоритм построения неизвестен.

Dict digest
    | Bit(256), дайджест словаря.
    | Текст дайджеста совпадает с именем словаря, который используется для распаковки файлов типа SLIM_ZST_DICT.
    | Специальное значение 0 в случае отсутствия словаря.
    | Алгоритм построения неизвестен.

Zstd stream
    Сжатая по алгоритму zstandard карта имен.

Пример разбора
==============

Файл tests/samples/nm
---------------------

.. drawio-image:: diagrams/nm_dump.drawio

Дайджесты
---------

.. list-table:: Дайджесты
    :header-rows: 1
    :align: left
    :widths: 20 80

    * - Имя
      - Дайджест, BE

    * - Names digest
      - C2FA9EF840FA12F9

    * - Dict digest
      - BFB732560AD45234690ACAD246D7B14C2F25AD418A146E5E7EF68BA3386A315C

----------
Карта имен
----------

Содержит имена и строки, общие для группы файлов типа SLIM, SLIM_ZST, SLIM_ZST_DICT.

Пример:

* ``tests/samples/names``

.. drawio-image:: diagrams/names.drawio

Names count
    VarInt, количество имен.

Names data size
    VarInt, размер массива имен в октетах, если names count > 0.

Names[Names count]
    | Массив CString имен, если names count > 0.
    | Идентификаторы имен по порядку чтения массива.

Пример разбора
==============

Файл tests/samples/names
------------------------

.. drawio-image:: diagrams/names_dump.drawio

Карта имен
----------

.. list-table:: Карта имен и строк
    :header-rows: 1
    :align: left

    * - Индекс
      - Имя
    * - 0x00
      - \'vec4f\'
    * - 0x01
      - \'int\'
    * - 0x02
      - \'long\'
    * - 0x03
      - \'alpha\'
    * - 0x04
      - \'str\'
    * - 0x05
      - \'bool\'
    * - 0x06
      - \'color\'
    * - 0x07
      - \'gamma\'
    * - 0x08
      - \'vec2i\'
    * - 0x09
      - \'vec2f\'
    * - 0x0a
      - \'transform\'
    * - 0x0b
      - \'beta\'
    * - 0x0c
      - \'float\'
    * - 0x0d
      - \'vec3f\'
    * - 0x0e
      - \'hello\'

--------------
Файл типа SLIM
--------------

Неавтономный файл. Имена и строки файла находятся в разделяемом файле имен.

Примеры:

* ``WarThunder/aces.vromfs.bin/config/es_order.blk``
* ``tests/samples/section_slim.blk``

.. drawio-image:: diagrams/slim.drawio

File type
    Int8ul, тип файла FileType.SLIM.

Names count
    | VarInt, количество имен
    | Файл не содержит встроенной карты имен, names count = 0

Blocks count
    VarInt, количество блоков в файле, включая корневой блок.

Parameters count
    VarInt, количество параметров в файле.

Parameters data size
    VarInt, размер массива длинных параметров в октетах, если есть длинные параметры.

Parameters data
    | Регион длинных параметров, если есть длинные параметры.
    | Смещение в структуре ParameterInfo от начала региона.

ParameterInfo[Parameters count]
    | Массив структур ParameterInfo, если parameters count > 0.
    | Идентификаторы параметров по порядку чтения массива.

BlockInfo[Block count]
    | Массив структур BlockInfo, включая корневой блок, если blocks count > 0.
    | Идентификаторы блоков по порядку чтения массива.
    | Блоки перечислены при обходе дерева блоков в ширину.

Пример разбора
==============

Файл tests/samples/section_slim.blk
-----------------------------------

.. drawio-image:: diagrams/section_slim_dump.drawio

Карта имен
----------

Использована карта имен ``tests/samples/nm``.

Карта имен, массив структур ParameterInfo и регион Parameters data
------------------------------------------------------------------

.. drawio-image:: diagrams/section_slim_param_info_array_and_params_data_dump.drawio

------------------
Файл типа SLIM_ZST
------------------

Неавтономный файл, сжатый по алгоритму zstandard. Имена и строки файла находятся в разделяемом файле имен.

Примеры:

* ``WarThunder/char.vromfs.bin/config/attachable.blk``
* ``tests/samples/section_slim_zst.blk``

.. drawio-image:: diagrams/slim_zst.drawio

File type
    Int8ul, тип файла FileType.SLIM_ZST

Zstd stream
    Сжатый по алгоритму zstandard файл типа SLIM без первого октета.

Пример разбора
==============

Файл tests/samples/section_slim_zst.blk
---------------------------------------

.. drawio-image:: diagrams/section_slim_zst_dump.drawio

-----------------------
Файл типа SLIM_ZST_DICT
-----------------------

Неавтономный файл, сжатый по алгоритму zstandard с использованием словаря. Имя словаря - дайджест словаря из файла nm
в base16 с расширением ``.dict``.

Примеры:

* ``WarThunder/aces.vromfs.bin/_allowedconfigoverrides.blk``
* ``tests/samples/section_slim_zst_dict.blk``

.. drawio-image:: diagrams/slim_zst_dict.drawio

File type
    Int8ul, тип файла FileType.SLIM_ZST_DICT

Zstd stream
    Сжатый по алгоритму zstandard файл типа SLIM без первого октета.

Пример разбора
==============

Файл tests/samples/section_slim_zst_dict.blk
--------------------------------------------

.. drawio-image:: diagrams/section_slim_zst_dict_dump.drawio
