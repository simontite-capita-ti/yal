import os
import logging
from lxml import etree
from collections import Counter
from texttree.texttree import walk_file_lang_pairs
from .tools import convert_to_valid_xml_unicode


log = logging.getLogger(__name__)

def copy_to_originals(src_map, path, langs):
    """TODO: Docstring for copy_to_originals.

    :src_map: TODO
    :returns: TODO

    """
    dir_counter = Counter()
    inv_map = dict((dst, src) for src, dst in src_map.items())
    for i, pair in enumerate(walk_file_lang_pairs(path, langs)):
        pair1 = pair[langs[0]]
        pair2 = pair[langs[1]]
        log.info('Copy TMX file %s, based on %s, %s', i+1, pair1, pair2)
        src_file = inv_map[pair1.path]
        src_dir = os.path.dirname(src_file)
        src_dir = os.path.basename(src_dir)
        target_path = '{}_aligned_{}_{}-{}.tmx'.format(src_dir, dir_counter[src_dir], langs[0], langs[1])
        dir_counter[src_dir] += 1
        target_path = os.path.join(os.path.dirname(src_file), target_path)

        # Build TMX file
        tmx = etree.Element('tmx', version='1.4')
        tmx.append(etree.Element(
            'header',
            datatype='PlainText',
            segtype='sentence',
            adminlang='{}-{}'.format(langs[0], langs[1])
        ))
        body = etree.Element('body')
        tmx.append(body)
        with open(pair1.path) as f1, open(pair2.path) as f2:
            for rec1, rec2 in zip(f1, f2):
                tu = etree.Element('tu')
                body.append(tu)

                tuv1 = etree.Element('tuv')
                tu.append(tuv1)
                tuv1.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = langs[0]
                seg = etree.Element('seg')
                tuv1.append(seg)
                seg.text = convert_to_valid_xml_unicode(rec1.strip())

                tuv2 = etree.Element('tuv')
                tu.append(tuv2)
                tuv2.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = langs[1]
                seg = etree.Element('seg')
                tuv2.append(seg)
                seg.text = convert_to_valid_xml_unicode(rec2.strip())

        with open(target_path, 'wb') as f:
            f.write(etree.tostring(tmx, pretty_print=True, xml_declaration=True, encoding='utf-8'))
