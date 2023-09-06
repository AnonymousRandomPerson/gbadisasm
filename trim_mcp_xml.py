import lxml.etree as ET
import yaml

def recursive_find_settings(tree):
    value_tags = tree.findall("VALUE")
    if len(value_tags) > 1:
        raise RuntimeError()
    elif len(value_tags) == 0:
        # nested settings
        name_tags = tree.findall("NAME")
        if len(name_tags) > 1:
            raise RuntimeError()

        cur_settings_children = []
        for elem in tree.iterchildren():
            elem_tag = str(elem.tag)
            if elem_tag == "SETTING":
                cur_settings_children.append(recursive_find_settings(elem))
            elif elem_tag not in {"NAME", "VALUE", "PANELDATA"} and elem.tag is not ET.Comment:
                raise RuntimeError(f"type(elem): {type(elem)}, elem.tag: {elem.tag}")

        if len(name_tags) == 1:
            name_tag = name_tags[0]
            cur_settings = {}
            cur_settings[name_tag.text] = cur_settings_children
        else:
            cur_settings = cur_settings_children
    else:
        name_tags = tree.findall("NAME")
        if len(name_tags) != 1:
            raise RuntimeError()

        name_tag = name_tags[0].text
        value_tag = value_tags[0].text
        #print(f"name_tag: {name_tag}, value_tag: {value_tag}")
        cur_settings = {name_tag: value_tag}

    return cur_settings

def gen_link_order_or_file_list(tree):
    paths = []
    print(f"tree: {tree}")
    for file in tree.iterchildren():
        if str(file.tag) == "NAME":
            continue
        path = file.find("PATH")
        if path is None:
            raise RuntimeError(f"file: {file}")
        path_text = file.find("PATH").text
        paths.append(path_text)

    return paths

#def gen_overlay_group_list(tree):
#    

def get_output(tree, desired_target_name, output_basename):
    for target in tree.xpath("//TARGET"):
        name = target.find("NAME")
        if name.text != desired_target_name:
            target.getparent().remove(target)
        else:
            correct_target = target

    #for bad in tree.xpath("//*[self::LINKORDER or self::FILELIST or self::OVERLAYGROUPLIST or self::TARGETORDER or self::GROUPLIST]"):
    #for bad in tree.xpath("//*[self::TARGETORDER or self::GROUPLIST]"):
    #    bad.getparent().remove(bad)

    tag_names = set()

    setting_list = tree.xpath("//SETTINGLIST")[0]
    settings_trimmed = recursive_find_settings(setting_list)

    link_order = gen_link_order_or_file_list(tree.xpath("//LINKORDER")[0])
    file_list = gen_link_order_or_file_list(tree.xpath("//FILELIST")[0])
    overlay = tree.xpath("//OVERLAY")
    if len(overlay) != 1:
        raise RuntimeError()

    overlay_list = gen_link_order_or_file_list(overlay[0])
    settings_trimmed.append({"LinkOrder": link_order})
    settings_trimmed.append({"FileList": file_list})
    settings_trimmed.append({"Overlay": overlay_list})
    #for elem in setting_list.iterchildren():
    #    tag_names.add(str(elem.tag))

    #print(settings_trimmed)

    with open(f"{output_basename}.yml", "w+") as f:
        yaml.safe_dump(settings_trimmed, f, indent=2)

    #print(", ".join(tag_names))
    return tree

def main():
    MODE = 0
    if MODE == 0:
        INPUT_XML = "NITRO_Runtime.mcp.xml"
        DESIRED_TARGET_NAME = "NITRO_Interworking_LE"
        OUTPUT_BASENAME = "NITRO_Runtime_modified"
    elif MODE == 1:
        INPUT_XML = "MSL C.NITRO.mcp.xml"
        DESIRED_TARGET_NAME = "MSL C Interworking LE"
        OUTPUT_BASENAME = "MSL_C_NITRO_modified"
    elif MODE == 2:
        INPUT_XML = "MSL Extras.NITRO.mcp.xml"
        DESIRED_TARGET_NAME = "MSL Extra Interworking LE"
        OUTPUT_BASENAME = "MSL_Extras_NITRO_modified"
    elif MODE == 3:
        INPUT_XML = "MSL C++.NITRO.mcp.xml"
        DESIRED_TARGET_NAME = "MSL C++ NITRO Interworking LE"
        OUTPUT_BASENAME = "MSL_CPP_NITRO_modified"
    else:
        raise RuntimeError("No mode selected!")

    with open(INPUT_XML, "rb") as f:
        contents = f.read()

    parser = ET.XMLParser(remove_blank_text=True, encoding="utf-8")
    root = ET.fromstring(contents, parser)
    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    tree = get_output(tree, DESIRED_TARGET_NAME, OUTPUT_BASENAME)
    output = ET.tostring(tree).decode("utf-8")

    with open(f"{OUTPUT_BASENAME}.mcp.xml", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
