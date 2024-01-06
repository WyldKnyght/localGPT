import os
import shutil
import click
import subprocess

from constants import (
    DOCUMENT_MAP,
    SOURCE_DIRECTORY
)

def logToFile(logentry):
   with open("crawl.log","a") as file1:
      file1.write(logentry + "\n")
   print(logentry + "\n")

@click.command()
@click.option(
    "--device_type",
    default="cuda",
    type=click.Choice(
        [
            "cpu",
            "cuda",
            "ipu",
            "xpu",
            "mkldnn",
            "opengl",
            "opencl",
            "ideep",
            "hip",
            "ve",
            "fpga",
            "ort",
            "xla",
            "lazy",
            "vulkan",
            "mps",
            "meta",
            "hpu",
            "mtia",
        ],
    ),
    help="Device to run on. (Default is cuda)",
)
@click.option(
    "--landing_directory",
    default="./LANDING_DOCUMENTS"
)
@click.option(
    "--processed_directory",
    default="./PROCESSED_DOCUMENTS"
)
@click.option(
    "--error_directory",
    default="./ERROR_DOCUMENTS"
)
@click.option(
    "--unsupported_directory",
    default="./UNSUPPORTED_DOCUMENTS"
)
def main(device_type, landing_directory, processed_directory, error_directory, unsupported_directory):
   paths = []

   os.makedirs(processed_directory, exist_ok=True)
   os.makedirs(error_directory, exist_ok=True)
   os.makedirs(unsupported_directory, exist_ok=True)

   for root, _, files in os.walk(landing_directory):
      for file_name in files:
         file_extension = os.path.splitext(file_name)[1]
         short_filename = os.path.basename(file_name)

         if not os.path.isdir(f"{root}/{file_name}"):
            if file_extension in DOCUMENT_MAP.keys():
               shutil.move(f"{root}/{file_name}", f"{SOURCE_DIRECTORY}/{short_filename}")
               logToFile(f"START: {root}/{short_filename}")
               process = subprocess.Popen(
                   f"python ingest.py --device_type={device_type}",
                   shell=True,
                   stdout=subprocess.PIPE,
               )
               process.wait()
               if process.returncode > 0:
                  shutil.move(
                      f"{SOURCE_DIRECTORY}/{short_filename}",
                      f"{error_directory}/{short_filename}",
                  )
                  logToFile(f"ERROR: {root}/{short_filename}")
               else:
                  logToFile(f"VALID: {root}/{short_filename}")
                  shutil.move(
                      f"{SOURCE_DIRECTORY}/{short_filename}",
                      f"{processed_directory}/{short_filename}",
                  )
            else:
               shutil.move(f"{root}/{file_name}", f"{unsupported_directory}/{short_filename}")

if __name__ == "__main__":
    main()
