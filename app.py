import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(
    page_title="Image Steganography App",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 Image Steganography App")
st.write("Hide secret text or images inside photos!")

def text_to_bits(text):
    return "".join(format(ord(c), "08b") for c in text)

def encode_text(image, secret_text):
    img = image.convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    full_text = secret_text + "###END###"
    bits = text_to_bits(full_text)
    total_pixels = arr.shape[0] * arr.shape[1] * 3
    if len(bits) > total_pixels:
        return None, "Text too long!"
    flat = arr.flatten()
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)
    result = flat.reshape(arr.shape)
    return Image.fromarray(result), "Success"

def decode_text(image):
    img = image.convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    flat = arr.flatten()
    bits = "".join(str(pixel & 1) for pixel in flat)
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        char = chr(int(byte, 2))
        chars.append(char)
        text_so_far = "".join(chars)
        if text_so_far.endswith("###END###"):
            return text_so_far[:-9]
    return "No hidden text found!"

def encode_image(cover, secret):
    cover  = cover.convert("RGB")
    secret = secret.convert("RGB")
    secret = secret.resize(cover.size)
    cover_arr  = np.array(cover,  dtype=np.uint8)
    secret_arr = np.array(secret, dtype=np.uint8)
    stego = (cover_arr & 0xF0) | (secret_arr >> 4)
    return Image.fromarray(stego)

def decode_image(stego):
    stego = stego.convert("RGB")
    arr   = np.array(stego, dtype=np.uint8)
    extracted = (arr & 0x0F) << 4
    return Image.fromarray(extracted)

def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

st.sidebar.title("Menu")
option = st.sidebar.radio(
    "Choose an option:",
    [
        "Home",
        "Hide Text in Image",
        "Extract Text from Image",
        "Hide Image in Image",
        "Extract Image from Image"
    ]
)

if option == "Home":
    st.header("Welcome!")
    st.write("This app hides secret messages inside images.")
    col1, col2 = st.columns(2)
    with col1:
        st.info("Hide Text inside any image")
        st.info("Hide Image inside another image")
    with col2:
        st.success("Extract hidden text from image")
        st.success("Extract hidden image from stego")
    st.write("Uses LSB - Least Significant Bit technique")

elif option == "Hide Text in Image":
    st.header("Hide Text in Image")
    uploaded = st.file_uploader(
        "Upload Cover Image",
        type=["jpg","jpeg","png"]
    )
    secret_text = st.text_area("Enter Secret Text:")
    if uploaded and secret_text:
        cover_img = Image.open(uploaded)
        st.image(cover_img,
                 caption="Cover Image",
                 use_column_width=True)
        if st.button("Hide Text Now"):
            result_img, msg = encode_text(
                cover_img, secret_text)
            if result_img:
                st.image(result_img,
                         caption="Stego Image",
                         use_column_width=True)
                st.success("Text hidden successfully!")
                st.download_button(
                    "Download Stego Image",
                    image_to_bytes(result_img),
                    "stego_text.png",
                    "image/png"
                )
            else:
                st.error(msg)

elif option == "Extract Text from Image":
    st.header("Extract Text from Image")
    uploaded = st.file_uploader(
        "Upload Stego Image",
        type=["jpg","jpeg","png"]
    )
    if uploaded:
        stego_img = Image.open(uploaded)
        st.image(stego_img,
                 caption="Stego Image",
                 use_column_width=True)
        if st.button("Extract Text Now"):
            result = decode_text(stego_img)
            st.success("Extraction Complete!")
            st.text_area("Hidden Message:", result)

elif option == "Hide Image in Image":
    st.header("Hide Image in Image")
    cover_file = st.file_uploader(
        "Upload Cover Image",
        type=["jpg","jpeg","png"],
        key="cover"
    )
    secret_file = st.file_uploader(
        "Upload Secret Image",
        type=["jpg","jpeg","png"],
        key="secret"
    )
    if cover_file and secret_file:
        cover_img  = Image.open(cover_file)
        secret_img = Image.open(secret_file)
        col1, col2 = st.columns(2)
        with col1:
            st.image(cover_img,
                     caption="Cover Image",
                     use_column_width=True)
        with col2:
            st.image(secret_img,
                     caption="Secret Image",
                     use_column_width=True)
        if st.button("Hide Image Now"):
            result_img = encode_image(
                cover_img, secret_img)
            st.image(result_img,
                     caption="Stego Image",
                     use_column_width=True)
            st.success("Image hidden successfully!")
            st.download_button(
                "Download Stego Image",
                image_to_bytes(result_img),
                "stego_image.png",
                "image/png"
            )

elif option == "Extract Image from Image":
    st.header("Extract Image from Image")
    uploaded = st.file_uploader(
        "Upload Stego Image",
        type=["jpg","jpeg","png"]
    )
    if uploaded:
        stego_img = Image.open(uploaded)
        st.image(stego_img,
                 caption="Stego Image",
                 use_column_width=True)
        if st.button("Extract Image Now"):
            result_img = decode_image(stego_img)
            st.image(result_img,
                     caption="Extracted Image",
                     use_column_width=True)
            st.success("Image extracted successfully!")
            st.download_button(
                "Download Extracted Image",
                image_to_bytes(result_img),
                "extracted.png",
                "image/png"
            )

st.write("---")
st.write("Made with Python and Streamlit")
st.write("Digital Image Processing Assignment")
