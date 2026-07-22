import argparse
import os
import shutil
import tarfile
from urllib.parse import urlparse
import requests
from tqdm import tqdm

# Stanford Dogs Image dataset
STANFORD_DOGS_URL = (
    "http://vision.stanford.edu/aditya86/ImageNetDogs/images.tar"
)

# Oxford Pets Images & Annotations
OXFORD_PET_IMAGES_URL = (
    "https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz"
)
OXFORD_PET_ANN_URL = (
    "https://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz"
)


def download_file(url: str, dest_folder: str) -> str:
    """
    Downloads a file showing progress.
    """
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(urlparse(url).path)
    filepath = os.path.join(dest_folder, filename)

    if os.path.exists(filepath):
        print(f"File {filename} already exists at {filepath}. Skipping download.")
        return filepath

    print(f"Downloading {url} to {filepath}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    block_size = 1024 * 1024  # 1 MB
    with open(filepath, "wb") as file, tqdm(
        total=total_size, unit="iB", unit_scale=True, desc=filename
    ) as bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            bar.update(size)

    print(f"Download complete: {filepath}")
    return filepath


def extract_tar(filepath: str, dest_folder: str) -> None:
    """
    Extracts tar / tar.gz files.
    """
    print(f"Extracting {filepath} to {dest_folder}...")
    os.makedirs(dest_folder, exist_ok=True)
    with tarfile.open(filepath) as tar:
        tar.extractall(path=dest_folder)
    print(f"Extraction complete for {filepath}")


def normalize_breed_name(name: str) -> str:
    """
    Standardizes breed names: lowercase, removes punctuation/prefixes, normalizes spacing.
    """
    name = name.lower().strip()
    # Strip Stanford Imagenet prefixes like 'n02085620-'
    if name.startswith("n") and "-" in name and name[1:9].isdigit():
        name = name.split("-", 1)[1]

    # Convert common delimiters to spaces
    name = name.replace("_", " ").replace("-", " ")

    # Map variant names (e.g. Japanese Spaniel is Japanese Chin, Pekinese is Pekingese)
    mapping = {
        "japanese spaniel": "japanese chin",
        "boston bull": "boston terrier",
        "pekinese": "pekingese",
        "german short haired pointer": "german shorthaired pointer",
        "cocker spaniel": "english cocker spaniel",
        "american pit bull terrier": "pit bull",
    }
    return mapping.get(name, name)


def merge_datasets(
    stanford_dir: str, oxford_dir: str, output_dir: str
) -> None:
    """
    Scans both datasets, matches identical breeds, and aggregates their images.
    """
    print("Beginning dataset merge...")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Parse Oxford Dogs from the list of annotations (to separate from cats)
    # Cat names in Oxford Pet start with an uppercase letter, Dog names are lowercase.
    # We can also parse annotations/list.txt: Class ID 1 is cat, 2 is dog.
    oxford_dogs = set()
    list_file = os.path.join(oxford_dir, "annotations", "list.txt")
    if os.path.exists(list_file):
        with open(list_file, "r") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.strip().split()
                if len(parts) >= 4:
                    image_name, class_id, species, breed_id = parts
                    if species == "2":  # 2 represents Dog
                        # extract breed from image name e.g. 'beagle_123' -> 'beagle'
                        breed_part = "_".join(image_name.split("_")[:-1])
                        oxford_dogs.add(breed_part.lower())

    print(f"Identified {len(oxford_dogs)} dog breeds from Oxford Pet annotations.")

    # Track all matched breeds
    merged_breed_counts = {}

    # Helper function to copy images
    def add_to_output(src_path: str, breed: str) -> None:
        target_breed_dir = os.path.join(output_dir, breed)
        os.makedirs(target_breed_dir, exist_ok=True)
        count = merged_breed_counts.get(breed, 0) + 1
        merged_breed_counts[breed] = count
        dest_filename = f"{breed}_{count}{os.path.splitext(src_path)[1]}"
        shutil.copy2(src_path, os.path.join(target_breed_dir, dest_filename))

    # 2. Process Stanford Dogs
    stanford_images_root = os.path.join(stanford_dir, "Images")
    if os.path.exists(stanford_images_root):
        for raw_breed in os.listdir(stanford_images_root):
            breed_path = os.path.join(stanford_images_root, raw_breed)
            if os.path.isdir(breed_path):
                normalized = normalize_breed_name(raw_breed)
                for img_name in os.listdir(breed_path):
                    if img_name.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".webp")
                    ):
                        add_to_output(
                            os.path.join(breed_path, img_name), normalized
                        )

    # 3. Process Oxford Pets
    oxford_images_root = os.path.join(oxford_dir, "images")
    if os.listdir(oxford_images_root):
        for img_name in os.listdir(oxford_images_root):
            if img_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                # Breed extraction from filename (e.g. 'boxer_123.jpg' -> 'boxer')
                filename_no_ext = os.path.splitext(img_name)[0]
                breed_part = "_".join(filename_no_ext.split("_")[:-1]).lower()

                if breed_part in oxford_dogs:
                    normalized = normalize_breed_name(breed_part)
                    add_to_output(
                        os.path.join(oxford_images_root, img_name), normalized
                    )

    print(f"Completed merging. Total unique breeds merged: {len(merged_breed_counts)}")
    print(f"Total merged images: {sum(merged_breed_counts.values())}")


def split_data(merged_dir: str, final_dir: str, val_split=0.15, test_split=0.15) -> None:
    """
    Divides the merged class folders into standard train/val/test partitions.
    """
    print(f"Splitting merged data in {merged_dir} into train/val/test splits...")
    import random
    random.seed(42)

    for partition in ["train", "val", "test"]:
        os.makedirs(os.path.join(final_dir, partition), exist_ok=True)

    for breed in os.listdir(merged_dir):
        breed_dir = os.path.join(merged_dir, breed)
        if not os.path.isdir(breed_dir):
            continue

        images = [
            f
            for f in os.listdir(breed_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]
        random.shuffle(images)

        n_images = len(images)
        n_test = int(n_images * test_split)
        n_val = int(n_images * val_split)

        test_imgs = images[:n_test]
        val_imgs = images[n_test : n_test + n_val]
        train_imgs = images[n_test + n_val :]

        splits = {"train": train_imgs, "val": val_imgs, "test": test_imgs}

        for split_name, split_list in splits.items():
            split_breed_dir = os.path.join(final_dir, split_name, breed)
            os.makedirs(split_breed_dir, exist_ok=True)
            for img in split_list:
                shutil.copy2(
                    os.path.join(breed_dir, img),
                    os.path.join(split_breed_dir, img),
                )

    print("Dataset partitioning finished.")


def main():
    parser = argparse.ArgumentParser(
        description="Dataset pipeline for download, merge, and split."
    )
    parser.add_argument(
        "--tmp-dir", default="./ml_tmp", help="Temp download directory"
    )
    parser.add_argument(
        "--output-dir", default="./ml/dataset", help="Output split dataset path"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create a small mock dataset offline for testing structure without download",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("Dry-run requested. Generating mock dataset structures...")
        # Make mock dataset
        for split in ["train", "val", "test"]:
            for breed in ["chihuahua", "beagle", "pug"]:
                os.makedirs(
                    os.path.join(args.output_dir, split, breed), exist_ok=True
                )
                # Create a small blank file
                with open(
                    os.path.join(
                        args.output_dir, split, breed, f"mock_{breed}_1.jpg"
                    ),
                    "wb",
                ) as f:
                    f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01")  # JPEG magic bytes
        print("Mock dataset generated successfully.")
        return

    # Download & Extract
    stanford_archive = download_file(STANFORD_DOGS_URL, args.tmp_dir)
    oxford_img_archive = download_file(OXFORD_PET_IMAGES_URL, args.tmp_dir)
    oxford_ann_archive = download_file(OXFORD_PET_ANN_URL, args.tmp_dir)

    stanford_extracted = os.path.join(args.tmp_dir, "stanford")
    oxford_extracted = os.path.join(args.tmp_dir, "oxford")

    extract_tar(stanford_archive, stanford_extracted)
    extract_tar(oxford_img_archive, oxford_extracted)
    extract_tar(oxford_ann_archive, oxford_extracted)

    merged_temp = os.path.join(args.tmp_dir, "merged")
    merge_datasets(stanford_extracted, oxford_extracted, merged_temp)
    split_data(merged_temp, args.output_dir)

    print("Cleaning temporary files...")
    shutil.rmtree(args.tmp_dir)
    print("Done!")


if __name__ == "__main__":
    main()
