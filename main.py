import re

from pdfbookmarker import PdfBookmarker


def main():
    bookmarker = PdfBookmarker("Linear-Algebra-Done-Right.pdf")
    bookmarker.display_contents()


if __name__ == '__main__':
    main()
