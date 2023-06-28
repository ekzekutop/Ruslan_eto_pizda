# загружаем библиотеки    streamlit run main.py
import streamlit as st
import easyocr
import cv2
import numpy as np
from io import StringIO
from PIL import Image
from PIL import ImageDraw
import tempfile
import os


# —-------------------Функция отрисовки границ bounding-box-ов---------------------
def draw_boxes(image, bounds, color='red', width=2):
    image = Image.open(image)  # чтобы загруженное img перевести в "путь" к нему (str)
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
    return st.image(image)


def enhance_contrast(image, contrast_limit=7.0):
    lab_img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab_img)

    clahe = cv2.createCLAHE(clipLimit=contrast_limit, tileGridSize=(8, 8))
    enhanced_l_channel = clahe.apply(l_channel)

    enhanced_lab_img = cv2.merge([enhanced_l_channel, a_channel, b_channel])
    enhanced_image = cv2.cvtColor(enhanced_lab_img, cv2.COLOR_LAB2BGR)

    return enhanced_image


def image_upload():
    st.subheader("Загрузка изображения")
    upload_img = st.file_uploader("Upload Images", type=["png", "jpg"])

    if upload_img is not None:
        # Создание временного файла
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        st.image(upload_img, use_column_width='auto')
        # Сохранение содержимого загруженного файла во временный файл
        temp_file.write(upload_img.read())
        temp_file.close()  # Закрытие временного файла

        # Улучшение контрастности изображения
        uploaded_image = cv2.imread(temp_file.name)
        enhanced_image = enhance_contrast(uploaded_image)
        enhanced_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        enhanced_pil_image = Image.fromarray(enhanced_image)
        enhanced_pil_image.save(enhanced_temp_file.name)
        enhanced_temp_file.close()  # Закрытие временного файла

        # —-------------------Header---------------------
        st.markdown('''<h1 style='text-align: center; color: white;'>
        Распознавание текста на изображениях</h1>''', unsafe_allow_html=True)

        img_ocr = enhanced_temp_file
        img_way = enhanced_temp_file.name

        # —-------------------Choosing language---------------------
        languages = ['ru', 'ar', 'az', 'be', 'bg', 'ch_tra', 'che', 'cs', 'de', 'en', 'es', 'fr', 'hi', 'hu', 'it', 'ja',
                    'la', 'pl', 'tr', 'uk', 'vi']
        chose_lang = st.multiselect('Выберите язык для распознавания:', languages)

        if st.button('Распознать текст с загруженного изображения'):
            if not chose_lang or not img_ocr:
                st.write('_Обработка приостановлена: загрузите изображение и/или выберите язык для распознавания._')
            else:
                reader = easyocr.Reader(chose_lang)

                # получаем координаты границ bounding-box-ов
                bounds = reader.readtext(img_way)

                # рисуем bounding-box-ы
                draw_boxes(img_way, bounds)
                result = reader.readtext(img_way, detail=0, paragraph=True)

                st.markdown('##### Распознанный текст:')
                for string in result:
                    st.write(string)

                # Удаление временных файлов
                os.remove(temp_file.name)
                os.remove(enhanced_temp_file.name)


try:
    image_upload()
except:
    pass
