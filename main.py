import moviepy as mp
import os
from typing import List


class VideoSummarizer:
    def __init__(self, input_path: str, output_path: str = None):
        """
        Initialize Video Summarizer

        Args:
            input_path (str): Path to the input video
            output_path (str, optional): Path to save the summary video
        """
        self.input_path = input_path
        self.output_path = output_path or self._generate_output_path()

        # Video properties
        try:
            self.video = mp.VideoFileClip(input_path)
        except Exception as e:
            raise ValueError(f"Error loading video file: {e}")
        
        self.fps = self.video.fps
        self.width = self.video.size[0]
        self.height = self.video.size[1]
        self.total_duration = self.video.duration

        print(f"Video Duration: {self.total_duration} seconds")
        print(f"Video FPS: {self.fps}")
        print(f"Video Width: {self.width}, Height: {self.height}")

        if self.total_duration == 0:
            raise ValueError("Invalid video file or zero duration detected.")

    def _generate_output_path(self) -> str:
        """
        Generate a default output path for the summary video

        Returns:
            str: Path for the output summary video
        """
        base, ext = os.path.splitext(self.input_path)
        return f"{base}_summary{ext}"

    def extract_video_segments(self, num_segments: int = 10, segment_duration: int = 3) -> List[mp.VideoClip]:
        """
        Extract video segments from the input video.

        Args:
            num_segments (int): Number of video segments to extract.
            segment_duration (int): Duration of each segment in seconds.

        Returns:
            List[mp.VideoClip]: List of video segments as moviepy VideoClips.
        """
        if self.total_duration == 0:
            raise ValueError("Cannot extract segments: video duration is zero.")

        # Check if total duration is less than segment count times segment duration
        total_required_duration = num_segments * segment_duration
        if self.total_duration < total_required_duration:
            print(f"Warning: The video duration is too short for {num_segments} segments of {segment_duration} seconds.")
            num_segments = int(self.total_duration // segment_duration)
            print(f"Reducing number of segments to {num_segments}.")

        segment_interval = max(1, self.total_duration / num_segments)
        video_clips = []

        for i in range(num_segments):
            start_time = i * segment_interval
            end_time = min(start_time + segment_duration, self.total_duration)
            print(f"Trying to extract segment {i}: {start_time} to {end_time} seconds")
            try:
                # Using subclipped() to extract segments
                video_clip = self.video.subclipped(start_time, end_time)
                video_clips.append(video_clip)
                print(f"Extracted segment {i}: {start_time} to {end_time} seconds")
            except Exception as e:
                print(f"Error extracting segment {i}: {e}")
                continue

        if not video_clips:
            print("No valid video segments extracted.")

        return video_clips

    def create_summary_video(self, video_segments: List[mp.VideoClip], summary_duration: int = 30) -> str:
        """
        Create a summary video from video segments.

        Args:
            video_segments (List[mp.VideoClip]): List of video segments.
            summary_duration (int): Desired summary duration in seconds.

        Returns:
            str: Path to the created summary video.
        """
        total_segments = len(video_segments)
        if total_segments == 0:
            raise ValueError("No video segments found. Cannot create summary.")

        adjusted_duration = summary_duration / total_segments

        try:
            # Set the duration for each clip using with_duration() instead of set_duration()
            clips_with_duration = [clip.with_duration(adjusted_duration) for clip in video_segments]

            # Concatenate segments
            final_clip = mp.concatenate_videoclips(clips_with_duration, method="compose")

            # Add audio if available
            try:
                if self.video.audio:
                    audio = self.video.audio.subclip(0, summary_duration)
                    final_clip = final_clip.set_audio(audio)
            except Exception as audio_error:
                print(f"Warning: Could not add audio to summary. Error: {audio_error}")

            # Write summary video
            final_clip.write_videofile(
                self.output_path,
                codec="libx264",
                audio_codec="aac",
                fps=self.fps
            )

            final_clip.close()

        except Exception as e:
            print(f"Error during summary video creation: {e}")

        finally:
            # Ensure cleanup of resources
            for clip in video_segments:
                clip.close()

        return self.output_path


def main():
    # Replace with your video path
    input_video_path = r'C:\jvn_codes\sen\video-summary\videoplayback.mp4'

    try:
        # Create summarizer
        summarizer = VideoSummarizer(input_video_path)

        # Extract video segments
        video_segments = summarizer.extract_video_segments(num_segments=5, segment_duration=3)  # Reduced segments

        if video_segments:
            # Create summary video
            summary_path = summarizer.create_summary_video(
                video_segments,
                summary_duration=30  # 10-second summary
            )

            print(f"Video summary created: {summary_path}")
        else:
            print("No valid video segments extracted.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
