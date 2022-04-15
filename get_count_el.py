from archicad import ACConnection
from typing import List, Dict
import pandas as pd
from collections import defaultdict

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities

builtin_property = ['ModelView_LayerName']
user_defined_property = [
    ('Электрика', 'Поз1'),
    ('Электрика', 'Поз2'),
    ('Электрика', 'Поз3'),
    ('Электрика', 'Поз4'),
    ('Электрика', 'Поз5')
]
table_col = ['element', 'id', 'layer', 'zone', 'name', 'gr_name', 'gen_el_gr']


def get_built_in_property_id(properties: List):
    if all(isinstance(prop, str) for prop in properties):
        return [acu.GetBuiltInPropertyId(prop) for prop in properties]
    if all(isinstance(prop, tuple) for prop in properties):
        return [acu.GetUserDefinedPropertyId(*prop) for prop in properties]
    else:
        raise TypeError('Type of elements in properties must be str or tuple(str)')


list_of_property_id = get_built_in_property_id(builtin_property) + \
                      get_built_in_property_id(user_defined_property)
classificationItem = acu.FindClassificationItemInSystem(
    'Классификация ARCHICAD', 'Розетки и выключатели')
elements = acc.GetElementsByClassification(classificationItem.classificationItemId)

property_values = acc.GetPropertyValuesOfElements(elements, list_of_property_id)
prop_dict = acu.GetPropertyValuesDictionary(elements, list_of_property_id)

elem_prop_value = [[key.elementId, *val.keys()] for key, val in prop_dict.items()]
prop_val_iter = (p_v.propertyValues for p_v in property_values)

df_prop_value = []
for elem in elem_prop_value:
    elem_buffer = [elem[0].guid]
    for index, p_v in enumerate(next(prop_val_iter)):
        elem[index + 1] = (elem[index + 1], p_v.propertyValue)
        elem_buffer.append(p_v.propertyValue.value)
    df_prop_value.append(elem_buffer)
count_el = defaultdict(int)
for val in df_prop_value:
    for el in val[2::]:
        if el != '  -':
            count_el[el.strip()] += 1
for k, v in sorted(count_el.items()):
    print(f'|{k:35}| {v}')

# df = pd.DataFrame(df_prop_value, columns=table_col)
# df = df.sort_values(by=['zone', 'name', 'gr_name', 'gen_el_gr'])
# df = df[df.layer.str.contains('мебель')]
# print(df)
# gb = df.groupby(['zone', 'name', 'gr_name'])[['id']].count()
# gb['id'] = [str(i) for i in range(1, len(gb['id']) + 1)]
# print(gb)
# df_out = pd.merge(df, gb, on=['zone', 'name', 'gr_name'])
# df_out['id_x'] = df_out['id_y']
# df_out = df_out.rename(columns={'id_x': 'id'})
# df_out = df_out.drop('id_y', axis=1)



