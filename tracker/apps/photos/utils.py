from io import BytesIO
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional

import cv2
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

    # Crop video to square
    # width, height = image.size
    # if width > height:
    #     left = (width - height) // 2
    #     top = 0
    #     right = left + height
    #     bottom = height
    # else:
    #     left = 0
    #     top = (height - width) // 2
    #     right = width
    #     bottom = top + width

    # return image.crop((left, top, right, bottom))
    return image


def generate_image_with_context(photo: Photo, name: Optional[str] = None) -> str:
    if not photo.activity:
        raise ValueError(f'Photo {photo.id} is not related to an activitiy')

    activity = photo.activity
    total_distance_traveled = activity.get_shoe_distance_display()
    distance = activity.get_distance_display()
    avg_pace = activity.average_pace
    created = timezone.localtime(activity.created).strftime('%Y-%m-%d %H:%M')

    image = get_prepared_image(photo)
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
    draw.rectangle((padding, padding, padding + 1000, padding + 340), fill=(0, 0, 0))
    draw.text((padding + text_padding, padding + text_padding), text, font=font)

    temp_dir = settings.MEDIA_ROOT / 'temp' / str(photo.category_id)
    temp_dir.mkdir(parents=True, exist_ok=True)
    if not name:
        name = str(photo.id)

    file_path = temp_dir / f'{name}.jpg'
    image.save(file_path)
    return str(file_path)


def generate_category_video(category: PhotoCategory) -> None:
    photos = category.photos.order_by('created')
    image_files = []
    for i, photo in enumerate(photos):
        path = generate_image_with_context(photo, i)
        image_files.append(path)

    frame = cv2.imread(image_files[0])
    height, width, _ = frame.shape
    video_name = 'output_video.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec to use
    fps = 1  # frames per second
    video_writer = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    # Loop through the image files and write them to the video
    for image_file in image_files:
        frame = cv2.imread(image_file)
        video_writer.write(frame)

    video_writer.release()
