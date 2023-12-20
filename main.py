from camera import start_camera, parse_output

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    match = parse_output("""12:35 Golden Vendetta (Gangplank): Gangplank - R
    12:36 [Team] Golden Vendetta (Gangplank): Stop this right now.
    12:37 Golden Vendetta (Gangplank) signals enemies are missing""")
    print(match.group(1))
    print(match.group(2))
    print(match.group(3))

    print(match.group(4))
    # start_camera()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
