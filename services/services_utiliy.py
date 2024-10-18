from pptx import Presentation
from io import BytesIO

def extract_first_image_from_slide(pptx_file):
    """Extract the first image from the first slide of a PPTX file."""
    try:
        # Load the PowerPoint presentation from the uploaded file
        ppt = Presentation(pptx_file)  # pptx_file is expected to be a file-like object, like BytesIO

        # Extract the first slide
        slide = ppt.slides[0]  # Change index if you want a specific slide

        # Iterate through shapes and find the first image
        for shape in slide.shapes:
            # Check if the shape contains an image (shape_type 13 indicates picture)
            if shape.shape_type == 13:  
                image = shape.image

                # Convert the image blob to a BytesIO object
                image_stream = BytesIO(image.blob)

                return image_stream  # Return the image binary data
        
        raise Exception("No image found on the first slide.")

    except Exception as e:
        raise Exception(f"Error extracting image from PPTX: {e}")