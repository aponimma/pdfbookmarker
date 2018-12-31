from pdfbookmarker import PdfBookmarker


def main():
    bookmarker = PdfBookmarker("Introduction-to-the-Theory-of-Computation.pdf")
    print(bookmarker.display_deviation())


if __name__ == '__main__':
    main()
