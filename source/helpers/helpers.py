from pathlib import Path

from siapy.entities.imagesets import SpectralImage, SpectralImageSet

from source.core import logger, settings


def _validate_filepaths_order(
    image_set_cam1: list[SpectralImage], image_set_cam2: list[SpectralImage]
):
    labels_cam1 = [
        image.filepath.stem.split(settings.labels_part_deliminator)[0]
        for image in image_set_cam1
    ]
    labels_cam2 = [
        image.filepath.stem.split(settings.labels_part_deliminator)[0]
        for image in image_set_cam2
    ]
    for label_cam1, label_cam2 in zip(labels_cam1, labels_cam2):
        if label_cam1 != label_cam2:
            raise ValueError("Check images, labels are not ordered correctly! ")


def read_spectral_images(
    images_dir: Path | str | None = None,
) -> tuple[list[SpectralImage], list[SpectralImage]]:
    if images_dir is None:
        images_dir = settings.images_dir
    file_paths = sorted(
        [Path(file) for file in Path(images_dir).glob("*") if file.is_file()]
    )

    header_paths = [
        path
        for idx, path in enumerate(file_paths)
        if file_paths[idx].suffixes[0] == settings.header_file_suffix
    ]
    image_paths = [
        path
        for idx, path in enumerate(file_paths)
        if file_paths[idx].suffixes[0] == settings.image_file_suffix
    ]

    image_set = SpectralImageSet.from_paths(
        header_paths=header_paths, image_paths=image_paths
    )

    # cameras_id = image_set.cameras_id

    image_set_cam1 = image_set.images_by_camera_id(settings.camera1_id)
    image_set_cam2 = image_set.images_by_camera_id(settings.camera2_id)

    _validate_filepaths_order(image_set_cam1, image_set_cam2)
    return image_set_cam1, image_set_cam2


def extract_labels_from_spectral_image(image: SpectralImage) -> list[str]:
    return image.filepath.name.split(settings.labels_part_deliminator)[0].split(
        settings.labels_between_deliminator
    )


def extract_labels_from_spectral_images(
    image_set_cam1: list[SpectralImage],
    image_set_cam2: list[SpectralImage],
) -> tuple[list[list[str]], list[list[str]]]:
    labels_cam1 = [
        extract_labels_from_spectral_image(image) for image in image_set_cam1
    ]
    labels_cam2 = [
        extract_labels_from_spectral_image(image) for image in image_set_cam2
    ]

    return labels_cam1, labels_cam2


def get_images_by_label(
    label: str,
    image_set_cam1: list[SpectralImage],
    image_set_cam2: list[SpectralImage],
    labels_cam1: list[list[str]],
    labels_cam2: list[list[str]],
) -> tuple[SpectralImage, SpectralImage, int, int]:
    index_cam1 = -1
    index_cam2 = -1
    for idx, labels_list in enumerate(labels_cam1):
        if label in labels_list:
            index_cam1 = idx
            break
    for idx, labels_list in enumerate(labels_cam2):
        if label in labels_list:
            index_cam2 = idx
            break

    if index_cam1 == -1:
        raise ValueError(f"Label for '{label}' was not found for camera 1.")
    if index_cam2 == -1:
        raise ValueError(f"Label for '{label}' was not found for camera 2.")

    image_cam1 = image_set_cam1[index_cam1]
    image_cam2 = image_set_cam2[index_cam2]

    logger.info(f"Extracted images for label: '{label}'")
    logger.info(f"Camera1 image path: '{image_cam1.filepath}'")
    logger.info(f"Camera2 image path: '{image_cam2.filepath}'")
    return image_cam1, image_cam2, index_cam1, index_cam2
