import random
import re

import fitz
import pdf2image
import pytesseract


class Entry:
    """
    A class representing an entry in a table of contents.
    """

    def __init__(self, title, page, level=1):
        self.title = title
        self.page = page
        self.level = level


class Contents:
    """
    A class representing a table of contents of a pdf book.
    """
    LEVEL_PATTERNS = {0: r'index|preface|references|bibliography|appendix|part|solutions',
                      1: [r'[A-Z]$|\d+$', r'\bChapter'],
                      2: [r'([a-zA-Z0-9]+)\.([a-zA-Z0-9]+$)', r'\D'],
                      3: [r'\d+\.\d+\.\d+$', r'(?!Chapter)(?!\.)\D+']}

    def __init__(self, filename, deviation, from_page, to_page):
        self.doc = fitz.Document(filename)
        self.from_page = from_page
        self.to_page = to_page
        self.count = 0
        self.level_patterns = dict()
        self.container = []
        self.deviation = deviation

    @property
    def container(self):
        """

        :return:
        """
        return self._container

    @container.setter
    def container(self, container):
        if container:
            self._container = container
        else:
            self._container = []

            def pdf_to_img(pg):
                """
                Convert pdf pg to an image.
                :param pg: the pdf page to convert.
                :return: an image representing this page.
                """
                page_doc = fitz.Document()
                page_doc.insertPDF(self.doc, from_page=pg.number, to_page=pg.number)
                page_bytes = page_doc.write()
                page_img = pdf2image.convert_from_bytes(page_bytes, dpi=350)
                return page_img

            if self.from_page == 0 and self.to_page == 0:
                start = 0
                end = self.doc.pageCount
            else:
                start = self.from_page
                end = self.to_page + 1

            for pageNum in range(start, end):
                page = self.doc.loadPage(pageNum)
                img = pdf_to_img(page)
                text = pytesseract.image_to_string(img[0],
                                                   config='-l eng --psm 6 --oem 1')

                if text.lower().find('contents') != -1:
                    if self.from_page == 0:
                        self.from_page = page.number

                    def is_valid_entry(line):
                        """
                        Check whether line is a valid entry in the table of contents.
                        :param line: the line to check.
                        :return: whether line is a valid entry in the table of contents.
                        """
                        if not line or line.isspace():
                            # print("1, {}".format(line))
                            return 0
                        if len(line.split()) < 2 and not line.isdigit():
                            # print("2, {}".format(line))
                            return 0
                        if line.lower().find('contents') != -1:
                            # print("3, {}".format(line))
                            return 0
                        if not line.split()[-1].isdigit():
                            if re.match(r'\D*\d+\D*', line.split()[-1]):
                                return 2
                            if re.match(Contents.LEVEL_PATTERNS[2][0], line.split()[0]):
                                return 3
                            else:
                                # print("4, {}".format(line))
                                return 0
                        return 1

                    def clean_title(raw_title):
                        """
                        Clean all irrelevant texts from raw_title if any.
                        :param raw_title: the raw text of an entry's title to clean.
                        :return: a cleaned title.
                        """
                        match = re.search(r'\.\s*\.+', raw_title)
                        if match:
                            index = match.start()
                            return raw_title[:index]
                        return raw_title

                    def set_level(t, current_level, visited_levels):
                        """

                        :param t:
                        :param current_level:
                        :param visited_levels:
                        """
                        serial_num = t.split()[0]
                        if re.match(r'[a-zA-Z]', serial_num):
                            if re.search(Contents.LEVEL_PATTERNS[0], t.lower()):
                                return 1

                        if current_level == 4:
                            current_level = 1

                        if visited_levels[current_level]:
                            return 1
                        else:
                            visited_levels[current_level] = True

                        if self.level_patterns.get(current_level) is None:
                            for p in Contents.LEVEL_PATTERNS[current_level]:
                                if re.match(p, serial_num) is not None:
                                    self.level_patterns[current_level] = p
                                    break
                            if self.level_patterns.get(current_level) is None:
                                current_level = 1
                                return set_level(t, current_level, visited_levels)
                            return current_level
                        else:
                            if re.match(self.level_patterns[current_level], serial_num) is None:
                                current_level += 1
                                return set_level(t, current_level, visited_levels)
                            else:
                                return current_level

                    c_level = 1
                    tmp_title = ""
                    for l in text.split('\n'):
                        if is_valid_entry(l):
                            if is_valid_entry(l) == 3:
                                tmp_title = l
                            else:
                                if tmp_title != "" and is_valid_entry(l) != 3:
                                    title = tmp_title + clean_title(" ".join(l.split()[:-1]))
                                    tmp_title = ""
                                else:
                                    tmp_title = ""
                                    title = clean_title(" ".join(l.split()[:-1]))
                                if is_valid_entry(l) == 2:
                                    page = int(re.findall(r'\d+', l.split()[-1])[0])
                                else:
                                    page = int(l.split()[-1])
                                level = set_level(title, c_level, {1: False, 2: False, 3: False})
                                c_level = level
                                entry = Entry(title, page, level)
                                self.add_entry(entry)

                else:
                    if self.from_page != 0 and self.to_page == 0:
                        self.to_page = page.number - 1
                        break

    @property
    def deviation(self):
        """
        The difference between the page number in the contents and its real location.
        """
        return self._deviation

    @deviation.setter
    def deviation(self, deviation):
        """
        Set the deviation of this pdf book.
        :param deviation: the value to set.
        """
        if deviation != 0:
            self._deviation = deviation
        else:
            index = random.randrange(self.count)
            entry = self.get_entry(index)
            for i in range(entry.page, self.doc.pageCount):
                page = self.doc.loadPage(i)
                text = page.getText('text').lower()
                if text.find(entry.title.lower()) != -1 or text.find(str(entry.page)) != -1:
                    self._deviation = page.number - entry.page
                    break
        # print(self.contents.deviation)

    def __iter__(self):
        return iter(self.container)

    def add_entry(self, entry):
        """
        Add a new entry into the table of contents.
        :param entry: the entry to add.
        """
        self.container.append(entry)
        self.count += 1

    def remove_entry(self, entry):
        """
        Remove an entry from table of the contents.
        :param entry: the entry to remove.
        """
        self.container.remove(entry)
        self.count -= 1

    def get_entry(self, index):
        """
        Get an entry from the table of the contents.
        :param index: the index of the entry.
        :return: the entry to get.
        """
        return self.container[index]

    def update_entry(self, index, **kwargs):
        """
        Update the information of an entry in the table of the contents.
        :param index: the index of the entry to update.
        :param kwargs:
        """
        if 'title' in kwargs:
            self.container[index].title = kwargs['title']
        if 'page' in kwargs:
            self.container[index].page = kwargs['page']
        if 'level' in kwargs:
            self.container[index].level = kwargs['level']
