# def get_decimal_coordinates(info):
#     for key in ['Latitude', 'Longitude']:
#         if 'GPS' + key in info and 'GPS' + key + 'Ref' in info:
#             e = info['GPS' + key]
#             print(f"**{e}")
#             ref = info['GPS' + key + 'Ref']
#             print(f"**{ref}")
#             info[key] = (e[0][0] / e[0][1] +
#                          e[1][0] / e[1][1] / 60 +
#                          e[2][0] / e[2][1] / 3600
#                          ) * (-1 if ref in ['S', 'W'] else 1)
#
#     if 'Latitude' in info and 'Longitude' in info:
#         return [info['Latitude'], info['Longitude']]


def format_dms_coordinates(coordinates):
    return f"{coordinates[0]}° {coordinates[1]}\' {coordinates[2]}\""


def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
    decimal_degrees = coordinates[0] + \
                      coordinates[1] / 60 + \
                      coordinates[2] / 3600

    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees

    return float(decimal_degrees)

