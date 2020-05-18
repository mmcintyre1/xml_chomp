from lxml import etree

# TODO ignore_ns should be a decorator
# TODO move cleaning methods to a cleaner class


class XmlChomp:
    def __init__(self, xml_input, recover=True):
        self.input = xml_input
        self.tree = self._read_input_to_tree(recover)

    def __str__(self):
        return etree.tostring(
            self.tree,
            encoding='unicode',
            method='xml',
            pretty_print=True
        )

    def __repr__(self):
        parser = etree.XMLParser(remove_blank_text=True)
        mini_xml = etree.fromstring(etree.tostring(self.tree), parser)

        return etree.tostring(
            mini_xml,
            encoding='unicode',
            method='xml'
        )

    def _read_input_to_tree(self, recover):
        """
        Reads input either from a string or a file-like object to an etree
        object and stores in an instance variable.
        :param recover: boolean - tries to recover if badly formed xml
        :return: None
        """
        parser = etree.XMLParser(recover=recover)
        try:
            return etree.parse(self.input, parser)
        except OSError:
            return etree.fromstring(self.input, parser)

    def _local_namer(self, xpath):
        """
        Helper function to replace xpath fields with local-name() entities,
        which is the way that namespaces are generally ignored.  Supports various ways
        of accesing data, but only xpath notation and not the more generic pathing
        lxml supports.

        More explicit examples of how things are transformed are available in the test suite.
        :param xpath: an xpath
        :return: a string with names replaced with /*[local-name()='example']
        """
        local_name_replacer = "/*[local-name()="
        xpath_parts = [tag_name.strip() for tag_name in xpath.split('/') if tag_name.strip()]

        final_parts = []
        for node in xpath_parts:
            if '[@' in node:
                tag, attr = self._split_attr(node)
                final_parts.append(f"{local_name_replacer}'{tag}']{attr}")
            # differentiate between attributes as part of a parent node and attributes to return
            elif '@' in node:
                final_parts.append(f"/{node}")
            else:
                final_parts.append(f"{local_name_replacer}'{node}']")
        return "".join(final_parts)

    @staticmethod
    def _split_attr(node):
        """

        :param node:
        :return:
        """
        try:
            tag, attr = node.split('[@')
        except ValueError:
            raise ValueError(f"{node} is not a correct attribute layout.  Try something like ./tag[@attr='abc']")
        return tag, f"[@{attr}"

    def _strip_tags(self, tag):
        """
        Replaces all tags by replacing their values with a generic value
        that is meant to have no collisions.
        # TODO figure out why I did it this way and not just used strip_tags
        :param tag: a string
        :return: None - modifies the instance tree in place
        """
        find = self._get_search_method(tag)
        delete_tag = "placeholderdeletiontag"

        for element in find(tag):
            element.tag = delete_tag

        etree.strip_tags(self.tree, delete_tag)

    def _get_search_method(self, tag):
        """
        Helper method to wrap a find method in either iterfind or xpath,
        based on how the tag passed in looks.

        If something like '/a/b/c' comes in, xpath will be used, but if './c'
        comes in iterfind will be used.
        :param tag:
        :return:
        """
        return self.tree.xpath if self._is_absolute_path(tag) else self.tree.iterfind

    @staticmethod
    def _is_absolute_path(path):
        """

        :param path:
        :return:
        """
        return not path.startswith('.')

    def get_doc_info(self):
        """
        Gets the markup type of a document.
        :return: the public markup type id
        """
        return self.tree.docinfo.public_id

    def get_all_tags(self):
        """
        Gets all tags in a tree.
        :return: a set of all tags
        # TODO does it return absolute path or just individual names?
        """
        all_tags = set()
        for element in self.tree.iter():
            all_tags.add(element.tag)

        return all_tags

    def count_all_counts(self):
        """
        Counts the occurrence of all tags.
        :return: a Counter() dictionary
        """
        pass

    def has_text(self, xpath, ignore_ns=False):
        """
        Checks if an xpath has any text in any of it's children nodes or
        in itself and returns a boolean.
        :param xpath: an xpath location to check
        :param ignore_ns: boolean - ignore namespaces if true
        :return: boolean
        """
        for e in self.tree.xpath(self._local_namer(xpath) if ignore_ns else xpath):
            for i in e.iter():
                if i.text:
                    return True
        return False

    def remove_xpath(self, tag, leave_values=False):
        """

        :param tag:
        :param leave_values:
        :return:
        """
        find = self._get_search_method(tag)
        for element in find(tag):
            if leave_values:
                self._strip_tags(tag)
            else:
                element.getparent().remove(element)

    def replace_tags(self, tag, replacement_text):
        """

        :param tag:
        :param replacement_text:
        :return:
        """
        find = self._get_search_method(tag)
        for r in find(tag):
            r.tail = replacement_text + r.tail if r.tail else replacement_text
        self.remove_xpath(tag, leave_values=True)

    def remove_all_tags(self):
        """

        :return:
        """
        return etree.tostring(self.tree, method="text", encoding="utf-8").decode("utf-8")

    def get_xpath_value(self, xpath, ignore_ns=False, check_type='text'):
        """

        :param xpath:
        :param ignore_ns:
        :param check_type:
        :return:
        """
        if self.tree is not None:
            try:
                data = self.tree.xpath(self._local_namer(xpath) if ignore_ns else xpath)
                if check_type == 'text':
                    return [value.text for value in data]
                elif check_type == 'attribute':
                    return data
            except (OSError, IndexError):
                return []

    def make_child_dict(self, xpath, ignore_ns=False):
        """

        :param xpath:
        :param ignore_ns:
        :return:
        """
        out_items = []
        for items in self.tree.xpath(self._local_namer(xpath) if ignore_ns else xpath):
            tmp_dict = {}
            for item in items:

                if ignore_ns:
                    tag = item.tag.split("}")[-1]
                else:
                    tag = item.tag

                tmp_dict[tag] = item.text

            out_items.append(tmp_dict)

        return out_items
