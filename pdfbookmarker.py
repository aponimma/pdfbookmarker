from contents import Contents


class PdfBookmarker:
    """
    A class automatically generating a table of contents using pdf bookmarks.
    """

    def __init__(self, filename, from_page=0, to_page=0, deviation=0):
        self.contents = Contents(filename=filename, from_page=from_page, to_page=to_page, deviation=deviation)

    @property
    def contents(self):
        """
        The table of contents of this pdf book.
        :return: the table of contents
        """
        return self._contents

    @contents.setter
    def contents(self, toc):
        """

        :param toc: the table of contents to set.
        """
        self._contents = toc

    def display_contents(self):
        """
        Display the table of the contents.
        :return: the table of the contents.
        """
        for entry in self.contents:
            print(entry.title, entry.page, entry.level)

    def display_deviation(self):
        """

        :return:
        """
        return self.contents.deviation

    def update_entry_title(self, index, title):
        """
        Update the title of an entry.
        :param index: the index of the entry to update.
        :param title: the new title.
        """
        self.contents.update_entry(index, title=title)

    def update_entry_page(self, index, page):
        """
        Update the page number of an entry.
        :param index: the index of the entry to update.
        :param page: the new page number.
        """
        self.contents.update_entry(index, page=page)

    def update_entry_level(self, index, level):
        """
        Update the level of an entry.
        :param index: the index of the entry to update.
        :param level: the new level.
        """
        self.contents.update_entry(index, level=level)
