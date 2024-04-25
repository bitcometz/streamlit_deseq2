import shutil
import os
import base64
import pandas as pd
import streamlit as st

# 清理函数：删除临时文件夹及其内容
def cleanup_tmpdir(tmpdir):
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)

def create_user_temp_dir(user_id):
    # 构造用户的临时文件夹路径
    temp_dir = "users/" + user_id
    # 创建用户临时文件夹（如果不存在）
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

# 读取图片文件
def read_image(file_path):
    with open(file_path, "rb") as img_file:
        img_bytes = img_file.read()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def create_download_zip(zip_directory, zip_path, filename):
    """
    zip_directory (str): path to directory  you want to zip 
    zip_path (str): where you want to save zip file
    filename (str): download filename for user who download this
    """
    shutil.make_archive(zip_path, 'zip', zip_directory)
    zip_file = zip_path + ".zip"

    with open(zip_file, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/zip;base64,{b64}" download=\'{filename}\'>\
            Download results \
        </a>'
        st.markdown(href, unsafe_allow_html=True)


def genComp(group1, group2, data, meta_file, user_dir):
    meta = pd.read_csv(meta_file)
    meta = meta[meta['group'].isin([group1, group2])]
    spls = [data.columns[0]] + meta['sample'].tolist()
    data = data[spls]
    data = data.reindex(columns=spls)
    #保存文件
    meta_com = os.path.join(user_dir, "meta.comps.csv")
    data_com = os.path.join(user_dir, "gene.comps.csv")

    meta.to_csv(meta_com, index=False)
    data.to_csv(data_com, index=False)

    return  data_com, meta_com
