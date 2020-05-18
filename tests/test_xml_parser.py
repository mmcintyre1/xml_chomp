import pytest


from utils import xml_parser


ns_xml_obj = xml_parser.Xml('./test_data/namespaced_xml.xml')


@pytest.mark.parametrize(
    'test_input,expected', [
        ("/component", "/*[local-name()='component']"),
        ("publicationMeta[@type='article']/doi", "/*[local-name()='publicationMeta'][@type='article']/*[local-name()='doi']"),
        ("/component/@name", "/*[local-name()='component']/@name"),
        ("/event[@type='firstOnline']/@date", "/*[local-name()='event'][@type='firstOnline']/@date"),
        ("/component/header/contentMeta/creators/creator[@creatorRole='author']/PersonName", "")
    ]
)
def test_local_namer(test_input, expected):
    assert ns_xml_obj._local_namer(test_input) == expected


@pytest.mark.parametrize(
    'test_input,expected', [
        ("/component/header/publicationMeta[@type='article']/doi", ['10.1002/ppul.24460']),
    ]
)
def test_get_xpath_value(test_input, expected):
    assert ns_xml_obj.get_xpath_value(test_input, ignore_ns=True) == expected

@pytest.mark.parametrize(
    'test_input,expected', [
        ("/component/header/publicationMeta/eventGroup/event[@type='firstOnline']/@date", ['2019-07-24']),
    ]
)
def test_get_xpath_attr(test_input, expected):
    assert ns_xml_obj.get_xpath_attr(test_input, ignore_ns=True) == expected


@pytest.mark.parametrize(
    'test_input,expected', [
        ("/component/header/contentMeta/creators/creator[@creatorRole='author']/personName",
         [{'degrees': 'MD, MSc, PhD', 'familyName': 'Loukou', 'givenNames': 'Ioanna'}]),
    ]
)
def test_make_child_dict(test_input, expected):
    assert ns_xml_obj.make_child_dict(test_input, ignore_ns=True) == expected



