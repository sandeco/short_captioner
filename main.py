from video_captioner import VideoCaptioner



captioner = VideoCaptioner(
    video_file="shorts-enxame.mp4", 
    output_file="with_transcript.mp4",
)

captioner.generate()
