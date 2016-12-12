def merge_src_maps(src_map1, src_map2):
    """TODO: Docstring for merge_src_maps.

    :src_map1: TODO
    :src_map2: TODO
    :returns: TODO

    """
    new_map = {}
    invert_map1 = dict((d, s) for s, d in src_map1.items())
    for src2, dst2 in src_map2.items():
        new_map[invert_map1[src2]] = dst2
    return new_map

def valide_xml_unicode_char(c):
    codepoint = ord(c)
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
    )

def convert_to_valid_xml_unicode(s):
    s = [c for c in s if valide_xml_unicode_char(c)]
    return ''.join(s)
