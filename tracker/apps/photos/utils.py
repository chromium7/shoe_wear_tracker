from io import BytesIO
from urllib.parse import urlparse
from typing import Optional

import cv2
import numpy as np
import httpx
from PIL import Image, ImageDraw, ImageFont

from django.conf import settings
from django.utils import timezone

from .models import Photo, PhotoCategory


def get_prepared_image(photo: Photo) -> Image:
    parsed_url = urlparse(photo.file.url)
    if parsed_url.scheme and parsed_url.netloc:
        response = httpx.get(photo.file.url)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(photo.file.url)

    return image


def center_shoes_in_image(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """
    Detects shoes in the image, centers them, and resizes the image to the target size with a black background.

    Args:
        image (Image.Image): The input PIL Image.
        target_size (Tuple[int, int]): Desired output size (width, height).

    Returns:
        Image.Image: The centered and resized PIL Image.
    """
    # Convert PIL Image to OpenCV format (numpy array)
    img_array = np.array(image)
    if len(img_array.shape) == 2:  # Grayscale image
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    elif img_array.shape[2] == 4:  # RGBA image
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)

    # Convert to grayscale for contour detection
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to separate the shoes from the background
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # If no contours are found, return the original image resized to target size
        img_array = cv2.resize(img_array, target_size, interpolation=cv2.INTER_AREA)
        return Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))

    # Find the largest contour (assuming the shoes are the largest object)
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x: int
    y: int
    w: int
    h: int
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Extract the region of interest (ROI) containing the shoes
    roi = img_array[y:y+h, x:x+w]

    # Calculate the scaling factor to fit the ROI into the target size while maintaining aspect ratio
    roi_h: int
    roi_w: int
    roi_h, roi_w = roi.shape[:2]
    scale: float = min(target_size[0] / roi_w, target_size[1] / roi_h)
    new_w: int = int(roi_w * scale)
    new_h: int = int(roi_h * scale)

    # Resize the ROI
    resized_roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create a black background image of the target size
    centered_img = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)

    # Calculate the position to center the resized ROI in the black background
    x_offset: int = (target_size[0] - new_w) // 2
    y_offset: int = (target_size[1] - new_h) // 2

    # Place the resized ROI in the center of the black background
    centered_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_roi

    # Convert back to PIL Image
    centered_pil_img = Image.fromarray(cv2.cvtColor(centered_img, cv2.COLOR_BGR2RGB))
    return centered_pil_img


def generate_image_with_context(photo: Photo, name: Optional[str] = None) -> str:
    activity = photo.activity
    if activity:
        total_distance_traveled = activity.get_shoe_distance_display()
        distance = activity.get_distance_display()
        avg_pace = activity.average_pace
        created = timezone.localtime(activity.created).strftime('%Y-%m-%d %H:%M')
    else:
        total_distance_traveled = 'N/A'
        distance = 'N/A'
        avg_pace = 'N/A'
        created = 'N/A'

    image = get_prepared_image(photo)
    # Define target size (use the original image size for consistency)
    target_size: tuple[int, int] = (image.width, image.height)

    # Center the shoes in the image
    image = center_shoes_in_image(image, target_size)

    width, _ = image.size
    # 2.5% padding
    padding =  0.025 * width
    text_padding = 25

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=64)
    text = (
        f'Total Distance: {total_distance_traveled}\n'
        f'Date: {created}\n'
        f'Distance: {distance}\n'
        f'Avg Pace: {avg_pace}'
    )

    # Calculate text box size
    text_bbox = draw.multiline_textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Draw background rectangle
    draw.rectangle(
        (padding, padding, padding + text_width + 2*text_padding, padding + text_height + 2*text_padding),
        fill=(0, 0, 0)
    )

    # Draw text
    draw.text((padding + text_padding, padding + text_padding), text, font=font)

    temp_dir = settings.MEDIA_ROOT / 'temp' / str(photo.category_id)
    temp_dir.mkdir(parents=True, exist_ok=True)
    if not name:
        name = str(photo.id)

    file_path = temp_dir / f'{name}.jpg'
    image.save(file_path)
    return str(file_path)


def generate_category_video(category: PhotoCategory, output_path: Optional[str] = None) -> None:
    photos = category.photos.order_by('created')
    image_files = []
    for i, photo in enumerate(photos):
        path = generate_image_with_context(photo, i)
        image_files.append(path)

    if not output_path:
        output_path = f'category_{category.id}_video.mp4'

    frame = cv2.imread(image_files[0])
    height, width, _ = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec to use
    fps = 1  # frames per second
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Loop through the image files and write them to the video
    for image_file in image_files:
        frame = cv2.imread(image_file)
        video_writer.write(frame)

    video_writer.release()
    return output_path
