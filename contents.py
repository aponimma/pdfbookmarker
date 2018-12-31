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
    def __init__(self, from_page=0, to_page=0):
        self.container = []
        self.from_page = from_page
        self.to_page = to_page
        self.count = 0

    def __iter__(self):
        return iter(self.container)

    def add_entry(self, entry):
        """
        Add a new entry into the table of contents.
        :param entry: the entry to add.
        """
        self.container.append(entry)
        self.count += 1

    def remove_bookmark(self, entry):
        """
        Remove an entry from table of the contents.
        :param entry: the entry to remove.
        """
        self.container.remove(entry)
        self.count -= 1

    def get_entry(self, index):
        """
        Get a entry from the table of the contents.
        :param index: the index of the entry.
        :return: the entry to get.
        """
        return self.container[index]


