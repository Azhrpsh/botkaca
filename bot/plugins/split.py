# GOAL:
# getting track for logging

import logging

LOGGER = logging.getLogger(__name__)

# GOAL:
# create split handler class

from os import path as os_path, remove as os_remove
import asyncio
from glob import glob
import ffmpeg

async def func(filepath, size):
    if not os_path.isfile(filepath):
        return False

    cmd = [
        "split",
        "--numeric-suffixes=1",
        "--suffix-length=3",
        f"--bytes={size}",
        filepath,
        filepath + "."
    ]
    LOGGER.debug(cmd)

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process.communicate()

    list = glob(filepath + ".*").sort()
    LOGGER.debug(list)
    return list

async def video(filepath, size):
    supported = ['.mp4','.mkv','.avi','.webm','.wmv','.mov']
    if not os_path.isfile(filepath):
        yield False
    
    file_path_name, file_ext = os_path.splitext(filepath)
    if not file_ext in supported:
        yield False

    probe = ffmpeg.probe(filepath)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    duration = video_stream["duration"]

    splited_duration = 0
    i = 0

    while splited_duration < duration:    
        i+=1
        out_file = file_path_name + ".{:03d}".format(i) + file_ext
        stream = ffmpeg.input(filepath).output(out_file,
            fs = str(size * 9/10),
            c = "copy",
            ss = str(splited_duration)
        )
        process = await ffmpeg.run_async(stream)
        await process.communicate()
        
        probe = ffmpeg.probe(filepath)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

        splited_duration += video_stream["duration"]
        
        yield out_file