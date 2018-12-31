from pdfbookmarker import PdfBookmarker


def main():
    bookmarker = PdfBookmarker("Introduction-to-the-Theory-of-Computation.pdf")
    bookmarker.set_contents()
    bookmarker.set_contents_deviation()


if __name__ == '__main__':
    main()
