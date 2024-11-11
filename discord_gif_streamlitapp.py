import streamlit as st
from rembg import remove
from PIL import Image, ImageSequence
import io
import os


# Function to save the optimized GIF
def save_gif(frames, duration, output_path='output.gif'):
    buffer = io.BytesIO()
    frames[0].save(
        buffer, format='GIF', save_all=True, append_images=frames[1:],
        loop=0, duration=duration, optimize=True
    )
    file_size_kb = buffer.tell() / 1024
    buffer.seek(0)

    if file_size_kb <= 256:
        with open(output_path, 'wb') as f:
            f.write(buffer.read())
        return True, buffer
    else:
        return False, None


# Streamlit app
st.title("GIF Optimizer")

st.write(
    "Upload a GIF file, and this app will optimize it by resizing, "
    "removing the background, and ensuring the file size is manageable."
)

# Upload GIF file
uploaded_file = st.file_uploader("Choose a GIF file", type=["gif"])

if uploaded_file is not None:
    # Open the GIF
    with Image.open(uploaded_file) as img:
        duration = img.info.get('duration', 100)  # Default duration if not provided
        output_frames = []

        # Process each frame of the GIF
        for frame in ImageSequence.Iterator(img):
            width, height = frame.size
            new_size = max(width, height)
            square_frame = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))
            square_frame.paste(frame, ((new_size - width) // 2, (new_size - height) // 2))

            # Resize the frame to a smaller size
            square_frame = square_frame.resize((128, 128), Image.LANCZOS)
            output_frames.append(square_frame)

        # Try to save the optimized GIF
        success, optimized_buffer = save_gif(output_frames, duration)

        if success:
            st.image(optimized_buffer, caption="Optimized GIF", use_column_width=True)
            st.download_button(
                label="Download Optimized GIF",
                data=optimized_buffer,
                file_name="optimized_output.gif",
                mime="image/gif"
            )
            st.success("GIF optimized successfully!")
        else:
            st.warning("GIF file size exceeds 256 KB. Further optimizations will be applied.")

            # Apply further optimizations: reduce colors and skip frames
            optimized_frames = [frame.convert("P", palette=Image.ADAPTIVE, colors=64) for frame in output_frames]
            success, optimized_buffer = save_gif(optimized_frames, duration)

            if success:
                st.image(optimized_buffer, caption="Further Optimized GIF", use_column_width=True)
                st.download_button(
                    label="Download Further Optimized GIF",
                    data=optimized_buffer,
                    file_name="further_optimized_output.gif",
                    mime="image/gif"
                )
                st.success("GIF optimized further and saved successfully!")
            else:
                st.warning("GIF still too large after color reduction. Applying frame skipping...")

                frame_skip = 2
                optimized_frames = []
                for i, frame in enumerate(output_frames):
                    if i % frame_skip == 0:
                        optimized_frames.append(frame)

                # Reduce the number of frames
                optimized_frames = [frame.convert("P", palette=Image.ADAPTIVE, colors=32) for frame in optimized_frames]
                success, optimized_buffer = save_gif(optimized_frames, duration * frame_skip)

                if success:
                    st.image(optimized_buffer, caption="Final Optimized GIF", use_column_width=True)
                    st.download_button(
                        label="Download Final Optimized GIF",
                        data=optimized_buffer,
                        file_name="final_optimized_output.gif",
                        mime="image/gif"
                    )
                    st.success("GIF optimized successfully after frame skipping!")
                else:
                    st.error("Unable to optimize the GIF further. Consider reducing the input size.")
