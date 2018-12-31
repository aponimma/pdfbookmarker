import fitz
import random
import pdf2image
import pytesseract
from contents import Entry
from contents import Contents


class PdfBookmarker:
    """
    A class automatically generating a table of contents using pdf bookmarks.
    """

    def __init__(self, filename):
        self.doc = fitz.Document(filename)
        self._contents = Contents()
        self._deviation = 0

    @property
    def contents(self):
        """
        The table of contents of this pdf book.
        :return: the table of contents
        """
        return self.contents.container

    @contents.setter
    def contents(self, table=None):
        """

        :param table: the table of contents to set.
        """
        if table is not None:
            self.contents = table
        else:
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

            for page in self.doc:
                img = pdf_to_img(page)
                text = pytesseract.image_to_string(img[0],
                                                   config='--psm 6 -c preserve_interword_spaces=1')
                if text.lower().find('contents') != -1:
                    if self.contents.from_page == 0:
                        self.contents.from_page = page.number

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
                        print(word)
                        if is_valid_entry(word):
                            title = clean_title(" ".join(word.split()[:-1]))
                            page = int(word.split()[-1])
                            entry = Entry(title, page)
                            self.contents.add_entry(entry)
                            # print("{}, {}".format(bookmark.title, int(bookmark.page)))
                else:
                    if self.contents.from_page != 0 and self.contents.to_page == 0:
                        self.contents.to_page = page.number - 1
                        break

    @property
    def deviation(self):
        """
        The difference between the page number in the contents and its real location.
        """
        return self.deviation

    @deviation.setter
    def deviation(self, value=0):
        """
        Set the deviation of this pdf book.
        :param value: the value to set.
        """
        if value != 0:
            self.contents.deviation = value
        else:
            index = random.randrange(self.contents.count)
            entry = self.contents.get_entry(index)
            for i in range(entry.page, self.doc.pageCount):
                page = self.doc.loadPage(i)
                text = page.getText('text').lower()
                if text.find(entry.title.lower()) != -1 or text.find(str(entry.page)) != -1:
                    self.contents.deviation = page.number - entry.page
                    break
        # print(self.contents.deviation)





