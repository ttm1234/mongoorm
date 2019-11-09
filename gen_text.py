def open_txt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        r = f.read()
        return r


def write_txt(filename, s):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(s)


def main():
    demo = open_txt('demo.py')
    # print(demo, type(demo))
    readme = open_txt('./gen_txt_raw/README.md')
    readme = readme.format(demo=demo)
    write_txt('README.md', readme)

    initfile = open_txt('./gen_txt_raw/mongoorm-__init__.py')
    initfile = initfile.format(demo=demo)
    write_txt('./mongoorm/__init__.py', initfile)


if __name__ == '__main__':
    main()
