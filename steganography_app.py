
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from google.colab import files
import ipywidgets as widgets
from IPython.display import display, clear_output

def text_to_bits(text):
    bits = ''.join(format(ord(c), '08b') for c in text)
    return bits

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def encode_text(image_path, secret_text, output_path="stego_text.png"):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    full_text = secret_text + "###END###"
    bits = text_to_bits(full_text)
    total_pixels = arr.shape[0] * arr.shape[1] * 3
    if len(bits) > total_pixels:
        print("Error: Text is too long for this image!")
        return None
    flat = arr.flatten()
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)
    result = flat.reshape(arr.shape)
    out_img = Image.fromarray(result)
    out_img.save(output_path)
    print(f"Text hidden successfully! Saved as: {output_path}")
    return output_path

def decode_text(image_path):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    flat = arr.flatten()
    bits = ''.join(str(pixel & 1) for pixel in flat)
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        char = chr(int(byte, 2))
        chars.append(char)
        text_so_far = ''.join(chars)
        if text_so_far.endswith("###END###"):
            result = text_so_far[:-9]
            print(f"Hidden message: {result}")
            return result
    print("No hidden text found!")
    return None

def encode_image(cover_path, secret_path, output_path="stego_image.png"):
    cover  = Image.open(cover_path).convert("RGB")
    secret = Image.open(secret_path).convert("RGB")
    secret = secret.resize(cover.size)
    cover_arr  = np.array(cover,  dtype=np.uint8)
    secret_arr = np.array(secret, dtype=np.uint8)
    stego = (cover_arr & 0xF0) | (secret_arr >> 4)
    out_img = Image.fromarray(stego)
    out_img.save(output_path)
    print(f"Image hidden successfully! Saved as: {output_path}")
    return output_path

def decode_image(stego_path, output_path="extracted_image.png"):
    stego = Image.open(stego_path).convert("RGB")
    arr   = np.array(stego, dtype=np.uint8)
    extracted = (arr & 0x0F) << 4
    out_img = Image.fromarray(extracted)
    out_img.save(output_path)
    print(f"Image extracted successfully! Saved as: {output_path}")
    return output_path

def show_images(title, images_dict):
    n = len(images_dict)
    fig, axes = plt.subplots(1, n, figsize=(5*n, 4))
    if n == 1:
        axes = [axes]
    for ax, (label, img_path) in zip(axes, images_dict.items()):
        img = Image.open(img_path)
        ax.imshow(img)
        ax.set_title(label, fontsize=11, fontweight='bold')
        ax.axis('off')
    plt.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.show()

def show_menu():
    print("=" * 45)
    print("   IMAGE STEGANOGRAPHY APPLICATION")
    print("=" * 45)
    print("1. Hide TEXT inside an Image")
    print("2. Extract TEXT from an Image")
    print("3. Hide IMAGE inside another Image")
    print("4. Extract IMAGE from Stego Image")
    print("5. Exit")
    print("=" * 45)

def run_app():
    while True:
        show_menu()
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            print("Upload your cover image:")
            uploaded = files.upload()
            if not uploaded:
                continue
            image_path = list(uploaded.keys())[0]
            secret_text = input("Enter secret text to hide: ")
            output = encode_text(image_path, secret_text, "stego_text.png")
            if output:
                show_images("Hide Text in Image",
                {"Cover Image": image_path, "Stego Image": output})
                files.download("stego_text.png")
        elif choice == "2":
            print("Upload stego image:")
            uploaded = files.upload()
            if not uploaded:
                continue
            image_path = list(uploaded.keys())[0]
            decode_text(image_path)
        elif choice == "3":
            print("Upload cover image:")
            uploaded1 = files.upload()
            if not uploaded1:
                continue
            cover_path = list(uploaded1.keys())[0]
            print("Upload secret image:")
            uploaded2 = files.upload()
            if not uploaded2:
                continue
            secret_path = list(uploaded2.keys())[0]
            output = encode_image(cover_path, secret_path, "stego_image.png")
            if output:
                show_images("Hide Image in Image",
                {"Cover Image": cover_path,
                 "Secret Image": secret_path,
                 "Stego Image": output})
                files.download("stego_image.png")
        elif choice == "4":
            print("Upload stego image:")
            uploaded = files.upload()
            if not uploaded:
                continue
            stego_path = list(uploaded.keys())[0]
            output = decode_image(stego_path, "extracted.png")
            if output:
                show_images("Extracted Hidden Image",
                {"Stego Image": stego_path,
                 "Extracted Image": output})
                files.download("extracted.png")
        elif choice == "5":
            print("Thank you for using Steganography App!")
            break
        else:
            print("Invalid choice! Enter 1 to 5 only.")

run_app()
