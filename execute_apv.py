import json
import git
import os
import subprocess
import shutil

config_file = "config.json"
android_prepare_vendor_repo = "https://github.com/AOSPAlliance/android-prepare-vendor.git"
out_dir = "out"

if __name__ == "__main__":
    os.makedirs(out_dir, exist_ok=True)
    git.Git(out_dir).clone(android_prepare_vendor_repo)
    with open(config_file) as f:
        config = json.load(f)
        for device in config['devices']:
            build_id = config['devices'][device]['build_id']
            print("running android-prepare-vendor for device {} with build_id {}".format(device, build_id))
            result = subprocess.run(["./out/android-prepare-vendor/execute-all.sh", "-d", device, "-b", build_id, "-o", "out"])
            if result.returncode != 0:
                print("android-prepare-vendor returned exit code {} for device {}", result.returncode, device)
                exit(1)

            shutil.copy("out/{}/{}/vendor/google_devices/{}/build_id.txt".format(device, build_id.lower(), device),
                                "{}/build_id.txt".format(device))
            shutil.copy("out/{}/{}/vendor/google_devices/{}/file_signatures.txt".format(device, build_id.lower(), device),
                                "{}/file_signatures.txt".format(device))
            shutil.copy("out/{}/{}/vendor/google_devices/{}/vendor-board-info.txt".format(device, build_id.lower(), device),
                                "{}/vendor-board-info.txt".format(device))

