from archicad import ACConnection

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities


prop_names = acc.GetAllPropertyNames()

for prop in prop_names:
    if prop.type == 'BuiltIn':
        builtin_property_id = acu.GetBuiltInPropertyId(prop.nonLocalizedName)
        details_of_properties = acc.GetDetailsOfProperties([builtin_property_id])
        print(f' {prop.nonLocalizedName} - {details_of_properties}')
