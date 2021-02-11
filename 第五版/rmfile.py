import os


def clear_json(): #清理.json檔
    dir_name = "./"
    test = os.listdir(dir_name)
    for item in test:
        
        if item.endswith(".json"):
            print(item)
            os.remove(os.path.join(dir_name, item))