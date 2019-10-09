# from plot.py
def renaming_with_version(base_file_name):
    file_exist = 0
    for f in os.listdir('static/img/'): 
        if f'{base_file_name}' in f:
            old_file_name = f
            file_exist = 1    
            break

    if file_exist == 1:
        digit_ind = []
        for i, l in enumerate(old_file_name):
            if l.isdigit():
                digit_ind.append(i)
        version = old_file_name[digit_ind[0]:digit_ind[-1]+1]
        new_version = str(int(version) + 1)
        new_file_name = old_file_name.replace(version, new_version)
        os.remove(f'static/img/{old_file_name}')

    elif file_exist == 0:
        new_file_name = f'{base_file_name}1.png'

    return new_file_name