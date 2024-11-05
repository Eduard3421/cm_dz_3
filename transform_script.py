import sys
import xml.etree.ElementTree as ET

def handle_comment(lines):
    while True:
        line = next(lines)
        if line.strip() == ')':
            break

def handle_dict(lines, parent):
    dict_element = ET.SubElement(parent, 'dict')
    while True:
        line = next(lines)
        if line.strip() == '}':
            break
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        # строки
        if value.startswith('@"') and value.endswith('"'):
            value = value[2:-1]
            ET.SubElement(dict_element, 'string').text = value
        # числа
        elif value.isdigit():
            ET.SubElement(dict_element, 'number').text = value
        # словари
        elif value.startswith('{'):
            handle_dict(lines, dict_element)
        else:
            print(f"Syntax error: Unknown value type for key '{key}'", file=sys.stderr)
            sys.exit(1)

def main(input_file, output_file):
    root = ET.Element('config')
    constants = {}
    with open(input_file, 'r') as file:
        lines = iter(file.readlines())
        for line in lines:
            line = line.strip()
            # пустые строки
            if not line:
                continue
            # комментарии
            if line.startswith('(comment'):
                handle_comment(lines)
                continue
            # словари
            elif line.startswith('{'):
                handle_dict(lines, root)
                continue
            # константы
            elif ':' in line:
                name, value = line.split(':', 1)
                name = name.strip()
                value = value.strip().rstrip(';')
                constants[name] = value
                ET.SubElement(root, 'constant', attrib={'name': name, 'value': value})
                continue
            # вычисление констант
            elif line.startswith('.[') and line.endswith('].'):
                const_name = line[2:-2]
                if const_name in constants:
                    value = constants[const_name]
                    root.append(ET.Element('computed_constant', attrib={'name': const_name, 'value': value}))
                else:
                    print(f"Syntax error: Unknown constant '{const_name}' for line '{line}'", file=sys.stderr)
                    sys.exit(1)
            # другие элементы
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                ET.SubElement(root, 'key', attrib={'name': key}).text = value
            else:
                print(f"Syntax error: Unknown syntax for line '{line}'", file=sys.stderr)
                sys.exit(1)

    # генерация XML файла
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='unicode', xml_declaration=True)

if __name__ == '__main__':
    if len(sys.argv)!= 3:
        print("Usage: python transform_script.py <input_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
    print(f"XML file generated as {sys.argv[2]}")