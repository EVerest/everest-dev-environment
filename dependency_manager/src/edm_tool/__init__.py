from edm_tool import edm


def get_parser():
    return edm.get_parser()


def main():
    edm.main(get_parser())
