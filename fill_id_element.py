from archicad import ACConnection
from typing import List, Dict
import pandas as pd

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities

builtin_property = ['General_ElementID', 'ModelView_LayerName']
user_defined_property = [('Мебель', 'Зона'), ('Мебель', 'Вид'), ('Мебель', 'Имя_группы'), ('Мебель', 'Гл_эл_гр')]
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
    'Классификация ARCHICAD', 'Мебель')
elements = acc.GetElementsByClassification(
    classificationItem.classificationItemId
)

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

df = pd.DataFrame(df_prop_value, columns=table_col)
df = df.sort_values(by=['zone', 'name', 'gr_name', 'gen_el_gr'])

gb = df.groupby(['zone', 'name', 'gr_name'])[['id']].count()
print(gb)
gb['id'] = [str(i) for i in range(1, len(gb['id']) + 1)]

df_out = pd.merge(df, gb, on=['zone', 'name', 'gr_name'])
df_out['id_x'] = df_out['id_y']
df_out = df_out.rename(columns={'id_x': 'id'})
df_out = df_out.drop('id_y', axis=1)


def get_dict_elem_value_from_data(data_frame):
    output_prop_value = data_frame[['element', 'id']].to_dict('split')['data']
    return {val[0]: val[1] for val in output_prop_value}


output_dict_values = get_dict_elem_value_from_data(df_out)


def generate_new_property_values_for_elements(old_elem_prop_value: List, new_prop_values: Dict):
    elem_output_prop_value = [(elem_val[0], elem_val[1][0], elem_val[1][1]) for elem_val in old_elem_prop_value]

    for el_val in elem_output_prop_value:
        if el_val[0].guid in new_prop_values:
            el_val[2].value = new_prop_values[el_val[0].guid]
    return [act.ElementPropertyValue(*element) for element in elem_output_prop_value]


new_element_property_values = generate_new_property_values_for_elements(elem_prop_value, output_dict_values)
acc.SetPropertyValuesOfElements(new_element_property_values)
