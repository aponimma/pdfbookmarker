import random
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

    def __init__(self, filename, deviation, from_page, to_page):
        self.doc = fitz.Document(filename)
        self.container = []
        self.from_page = from_page
        self.to_page = to_page
        self.count = 0

        def pdf_to_img(pg):
            """
            Convert pdf pg to an image.
            :param pg: the pdf page to convert.
            :return: an image representing this page.
            """
            page_doc = fitz.Document()
            page_doc.insertPDF(self.doc, from_page=pg.number, to_page=pg.number)
            page_bytes = page_doc.write()
            page_img = pdf2image.convert_from_bytes(page_bytes, dpi=300)
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
                                               config='--psm 6 -c preserve_interword_spaces=1')
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
                        # print("1, {}".format(entry))
                        return False
                    if len(line.split()) < 2:
                        # print("2, {}".format(entry))
                        return False
                    if line.lower().find('contents') != -1:
                        # print("3, {}".format(entry))
                        return False
                    if not line.split()[-1].isdigit():
                        # print("4, {}".format(entry))
                        return False
                    return True

                def clean_title(raw_title):
                    """
                    Clean all irrelevant texts from raw_title if any.
                    :param raw_title: the raw text of an entry's title to clean.
                    :return: a cleaned title.
                    """
                    index = raw_title.find('..')
                    if index != -1:
                        return raw_title[:index]
                    return raw_title

                for word in text.split('\n'):
                    if is_valid_entry(word):
                        title = clean_title(" ".join(word.split()[:-1]))
                        page = int(word.split()[-1])
                        entry = Entry(title, page)
                        self.add_entry(entry)
                        # print("{}, {}".format(entry.title, entry.page))
            else:
                if self.from_page != 0 and self.to_page == 0:
                    self.to_page = page.number - 1
                    break

        self.deviation = deviation

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
