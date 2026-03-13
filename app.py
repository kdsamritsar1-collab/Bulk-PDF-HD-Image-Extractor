import streamlit as st
import fitz  # PyMuPDF
import io
import os
import time
from zipfile import ZipFile

# पेज सेटअप
st.set_page_config(page_title="Bulk HD Image Extractor", page_icon="🖼️", layout="wide")

# सुंदर डिजाइन के लिए CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; font-weight: bold; }
    .img-card { border: 1px solid #ddd; border-radius: 10px; padding: 5px; background: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Bulk HD PDF Image Extractor & Preview")
st.write("PDF अपलोड करें, फोटो देखें और हाई-क्वालिटी में डाउनलोड करें।")
st.divider()

# मल्टीपल फाइल अपलोडर
uploaded_files = st.file_uploader(
    "अपनी PDF फाइलें चुनें (Drag & Drop)", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    images_list = []
    total_files = len(uploaded_files)
    
    # प्रोग्रेस बार
    my_bar = st.progress(0, text="प्रोसेसिंग शुरू हो रही है...")
    
    for index, uploaded_file in enumerate(uploaded_files):
        base_name = os.path.splitext(uploaded_file.name)[0]
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        for page_idx in range(len(pdf_document)):
            page = pdf_document[page_idx]
            image_info = page.get_images(full=True)

            for img_idx, img in enumerate(image_info):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                img_name = f"{base_name}_P{page_idx+1}_I{img_idx+1}.{image_ext}"
                
                images_list.append({
                    "data": image_bytes,
                    "name": img_name
                })
        
        # प्रोग्रेस अपडेट
        percent_complete = (index + 1) / total_files
        my_bar.progress(percent_complete, text=f"प्रोसेसिंग: {index + 1}/{total_files} फाइलें")

    if images_list:
        st.success(f"कुल {len(images_list)} फोटो मिलीं!")
        
        # डाउनलोड सेक्शन (सबसे ऊपर ताकि ढूंढना न पड़े)
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            for img in images_list:
                zip_file.writestr(img["name"], img["data"])
        
        st.download_button(
            label=f"📥 सभी {len(images_list)} HD फोटो डाउनलोड करें (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="Bulk_HD_Extracted_Images.zip",
            mime="application/zip"
        )
        
        st.divider()
        
        # --- Thumbnail Gallery Section ---
        st.subheader("🖼️ Image Preview Gallery")
        
        # ग्रिड सिस्टम (एक लाइन में 4 फोटो)
        cols = st.columns(4)
        for i, img in enumerate(images_list):
            with cols[i % 4]:
                st.image(img["data"], caption=img["name"], use_container_width=True)
                
    else:
        st.error("अपलोड की गई फाइलों में कोई इमेज नहीं मिली।")
    
    time.sleep(1)
    my_bar.empty()

st.divider()
st.caption("Developed for @ruhanijot | Advanced Batch PDF Tool with Live Preview")