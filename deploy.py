import os
import shutil
import getpass


files = ["project_stats.plugin"]
folders = ["project_stats"]
script_path = os.path.dirname(os.path.realpath(__file__))
usr = getpass.getuser()

for fl in files:
    dst_path = "/home/{}/.local/share/gnome-builder/plugins/{}".format(usr, fl)
    shutil.copyfile(fl, dst_path)

for fldr in folders:
    dst_path = "/home/{}/.local/share/gnome-builder/plugins/{}"
    dst_path = dst_path.format(usr, fldr)
    if os.path.isdir(dst_path) == False:
        os.makedirs(dst_path)

    walk_dir = "{}/{}".format(script_path, fldr)
    for root, subfolders, files in os.walk(walk_dir):
        for file in files:
            src_path = "{}/{}".format(root, file)
            dst_path = "/home/{}/.local/share/gnome-builder/plugins/{}/{}"
            dst_path = dst_path.format(usr, fldr, file)
            shutil.copy(src_path, dst_path)

