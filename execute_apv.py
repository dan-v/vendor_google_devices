import json
import git
import os
import subprocess
import shutil
import logging
import concurrent.futures

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

config_file = "config.json"
android_prepare_vendor_repo = "https://github.com/AOSPAlliance/android-prepare-vendor.git"
out_dir = "out"

def execute_apv(device, build_id):
    logging.info("running android-prepare-vendor for device {} with build_id {}".format(device, build_id))
    result = subprocess.run(["./out/android-prepare-vendor/execute-all.sh", "-d", device, "-b", build_id, "-o", "out"])
    if result.returncode != 0:
        raise Exception("android-prepare-vendor returned exit code {} for device {}", result.returncode, device)

    shutil.copy("out/{}/{}/vendor/google_devices/{}/build_id.txt".format(device, build_id.lower(), device),
                "{}/build_id.txt".format(device))
    shutil.copy("out/{}/{}/vendor/google_devices/{}/file_signatures.txt".format(device, build_id.lower(), device),
                "{}/file_signatures.txt".format(device))
    shutil.copy("out/{}/{}/vendor/google_devices/{}/vendor-board-info.txt".format(device, build_id.lower(), device),
                "{}/vendor-board-info.txt".format(device))
    shutil.rmtree("out/{}".format(device), ignore_errors = False)

if __name__ == "__main__":
    os.makedirs(out_dir, exist_ok=True)
    git.Git(out_dir).clone(android_prepare_vendor_repo)
    with open(config_file) as f:
        config = json.load(f)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_apv = {executor.submit(execute_apv, device, config['devices'][device]['build_id']): device for device in config['devices']}
            for future in concurrent.futures.as_completed(future_apv):
                data = future.result()
