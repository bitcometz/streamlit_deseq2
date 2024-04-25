import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import multipletests
import numpy as np
import os
import subprocess
import tempfile
import atexit
import plotly.graph_objects as go
import plotly.express as px
from helpers.file_handling import *


def showSGR():
    singleron_base64 = read_image("src/singleron.png")
    with st.sidebar:
        st.markdown("---")

        st.markdown(
            f'<div style="margin-top: 0.25em; text-align: left;"><a href="https://singleron.bio/" target="_blank"><img src="data:image/png;base64,{singleron_base64}" alt="Homepage" style="object-fit: contain; max-width: 174px; max-height: 41px;"></a></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '''
            sessupport@singleronbio.com
            '''
        )

def get_sessionID():
    from streamlit.runtime import get_instance
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    runtime      = get_instance()
    session_id   = get_script_run_ctx().session_id
    session_info = runtime._session_mgr.get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session.id

def binaryswitch(session_state, key):
    if session_state[key] is True:
        session_state[key] = False
    else:
        session_state[key] = True

# Visualize differential expression results
def plot_de_results(results, down_x, up_x, up_y):

    results['log10padj'] = -np.log10(results['padj'] + 1e-100)
    fig = go.Figure()
    trace1 = go.Scatter(
        x=results['log2FoldChange'],
        y=results['log10padj'],
        mode='markers',
        name='comp1',
        hovertext=list(results.index)
    )
    # 根据条件设置颜色
    colors = []
    for i in range(len(results)):
        if results.iloc[i]['log2FoldChange'] < down_x and results.iloc[i]['log10padj'] > up_y:
            colors.append('blue')  # 蓝色
        elif results.iloc[i]['log2FoldChange'] > up_x and results.iloc[i]['log10padj'] > up_y:
            colors.append('red')  # 红色
        else:
            colors.append('gray')  # 灰色
    trace1.marker.color = colors
    fig.add_trace(trace1)
    # 添加虚线
    fig.add_shape(type="line", x0=down_x, y0=0, x1=down_x, y1=max(results['log10padj']), line=dict(color="green", width=1, dash="dash"))
    fig.add_shape(type="line", x0=up_x, y0=0, x1=up_x, y1=max(results['log10padj']), line=dict(color="green", width=1, dash="dash"))
    fig.add_shape(type="line", x0=min(results['log2FoldChange']), y0=up_y, x1=max(results['log2FoldChange']), y1=up_y, line=dict(color="green", width=1, dash="dash"))

    fig.update_layout(
        title='Volcano plot',
        xaxis_title="Log2 Fold Change",
        yaxis_title="-Log10 Adjusted P-value"
    )
    return fig

# Main function to run the app
def main():

    # initial variables
    default_variables = {
        "showData": False,
        "running": False,
        "zipResults": False,
        "showVolca": False,
        "showTable": False,
        "dataOK": False,
        "dataSource": None,
        "group1": None,
        "group2": None
    }
    for key, value in default_variables.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Show Welcon page
    st.sidebar.title("Bulk RNA-Seq Differential Expression Analysis")
    st.sidebar.markdown("### Inputs")
    add_selectbox = st.sidebar.selectbox(
        "What data would you like to use for analysis?",
        ("Demo", "Upload new"),
        index=None, placeholder="Please select ..."
    )
    if add_selectbox is None:
        st.title("Welcome !!!")
        st.write("Please select the inputs from the right slidebar!")
        showSGR()
        st.stop()

    ## 重要的文件不能放到临时文件夹
    user_id   = get_sessionID()
    user_dir  = create_user_temp_dir(user_id)
    meta_save = os.path.join(user_dir, "meta.csv")
    out_file  = os.path.join(user_dir, "res.csv")
    ## app重启后删掉相关文件夹
    atexit.register(cleanup_tmpdir, user_dir)

    # delete files after execution
    with tempfile.TemporaryDirectory() as temp_dir:

        if add_selectbox == "Demo":
            exp_file  = 'demo/gene.csv'
            meta_file = 'demo/meta.csv'
            data      = pd.read_csv(exp_file)
            meta      = pd.read_csv(meta_file)
            st.session_state['dataSource'] = "Demo"
            st.write()

        else:
            st.subheader("Upload your RNA-Seq data (CSV format)")
            exp_file  = st.file_uploader("Choose a CSV file for gene expression",   type="csv")
            st.write("Note: The first column of the matrix contains gene names, followed by the expression matrix of each sample, with column names representing the sample names.")
            meta_file = st.file_uploader("Choose a CSV file for group comparisons", type="csv")
            st.write("Note: This file contains grouping information. The first column is the sample name, with column name \"sample\". The values in the first column correspond to the expression matrix of the samples mentioned earlier. The second column contains grouping information with column name \"group\".")

            # 确认客户上传了文件
            if exp_file is not None and meta_file is not None:
                data      = pd.read_csv(exp_file)
                exp_file  = os.path.join(temp_dir, "gene.csv")
                data.to_csv(exp_file,  index=False)
                meta      = pd.read_csv(meta_file)
                meta_file = os.path.join(temp_dir, "meta.csv")
                meta.to_csv(meta_file, index=False)
                st.session_state['dataSource'] = "User"

        # Show gene expressions:
        if exp_file is not None:
            show_data = st.sidebar.checkbox("Show gene expressions", value=st.session_state['showData'], on_change=binaryswitch, args = (st.session_state, 'showData',))
            if show_data:
                st.subheader("gene expression (Top 6 rows)")
                st.write(data.head(6))
        
        ## 数据好了直接展示配置信息
        if meta_file is not None:
            st.subheader("sample ~ group")
            if not st.session_state["dataOK"]:
                st.write("You can modify the table below. Please ensure that the first column is named 'sample' and the second column is named 'group'.")
            edited_meta = st.data_editor(
                meta,
                hide_index=True,
            )

        ## 此处确认数据ok然后进入下面的环节
        if not st.session_state["dataOK"]:
            if st.button("Confirm meta info"):
                if exp_file is None:
                    st.write("Please input the gene expression file")
                    st.stop()
                if meta_file is None:
                    st.write("Please input the meta sample ~ group file")
                    st.stop()

                # 检查sample是否都在表达矩阵中
                for sample in edited_meta["sample"].unique():
                    if sample not in data.columns:
                        st.write(sample + " not found in gene expression, please modify the meta file")
                        st.stop()

                st.write("Check : all the samples are found in gene expression !")
                edited_meta.to_csv(meta_save, index=False)
                st.session_state["dataOK"] = True
        


        ## 数据确认后进入下面的环节：
        if st.session_state["dataOK"]:
            # Running parameters
            st.sidebar.markdown("### Running")
            # 提取数据做比较
            st.sidebar.markdown("Choose groups for comparisons:")
            col1, col2, col3 = st.sidebar.columns([3, 0.6, 3])
            # 获取组别列表
            group_list  = meta["group"].unique()

            st.session_state["group1"] = col1.selectbox("group1", group_list, index=None, placeholder="Please select ...", label_visibility="collapsed")
            col2.markdown("VS")
            st.session_state["group2"] = col3.selectbox("group2", group_list, index=None, placeholder="Please select ...", label_visibility="collapsed")
            st.write(
                """<style>
                [data-testid="stHorizontalBlock"] {
                    align-items: center;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            if st.session_state["group1"] is None or st.session_state["group2"] is None:
                st.info('Please select group1 vs group2 from the right slidebar', icon="ℹ️")
                st.stop()
            elif st.session_state["group1"] == st.session_state["group2"]:
                st.info('Group1 cannot be equal to group2', icon="ℹ️")
                st.stop()

            else:
                
                st.write("You have chosen:\n {} vs {}".format(st.session_state["group1"], st.session_state["group2"]))

            # Button to trigger R script execution
            if st.sidebar.button('Run DESeq2 for comparisons'):
                # 生成输入文件
                exp_comp, meta_comp = genComp(st.session_state["group1"], st.session_state["group2"], data, meta_save, user_dir)

                # Call the function to run R script
                process1       = subprocess.Popen(["Rscript", "DESeq2.r", exp_comp, meta_comp, out_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return_code    = process1.wait()
                stdout, stderr = process1.communicate()
                if return_code == 0:
                    st.session_state['running'] = True
                    st.write('DESeq2 executed successfully!')
                    st.write('You can click on the button of the right sidebar to view more results.')
                else:
                    st.write('DESeq2 runnning failed!')
                    st.write("please check your data !")


            if st.session_state['running']:
                results  = pd.read_csv(out_file)
                # Display differential expression results
                st.sidebar.markdown("### Tables")
                show_table = st.sidebar.checkbox("Show deseq2 tables", value=st.session_state['showTable'], on_change=binaryswitch, args = (st.session_state, 'showTable',))
                if show_table:
                    st.subheader("Differential Expression Results (top 4 rows)")
                    st.write(results.head(4))

                # Vocalno plots
                st.sidebar.markdown("### Plots")
                df = pd.DataFrame(
                    [
                       {"volcano plot": "Log2FC for Down genes <", "editable": -2},
                       {"volcano plot": "Log2FC for Up genes >",  "editable": 2},
                       {"volcano plot": "-Log10 Padj for sig >", "editable": 5},
                   ]
                )
                edited_df = st.sidebar.data_editor(
                    df,
                    column_config={
                        "volcano plot": "volcano plot",
                        "editable": st.column_config.NumberColumn(
                            "editable",
                            help="These parameters will affect the outcome of the plot.",
                            min_value=-100, max_value=100, step=1,
                            format="%d ⭐",
                        ),
                    },
                    disabled=["volcano plot"],
                    hide_index=True,
                )
                down_x = edited_df[edited_df["volcano plot"] == "Log2FC for Down genes <"]["editable"].iloc[0]
                up_x   = edited_df[edited_df["volcano plot"] == "Log2FC for Up genes >"]["editable"].iloc[0]
                up_y   = edited_df[edited_df["volcano plot"] == "-Log10 Padj for sig >"]["editable"].iloc[0]


                show_volca = st.sidebar.checkbox("Show volcano", value=st.session_state['showVolca'], on_change=binaryswitch, args = (st.session_state, 'showVolca',))
                if show_volca:
                    st.subheader("Visualizations")
                    st.write("Set parameters for significant points:")
                    fig    = plot_de_results(results, down_x, up_x, up_y)
                    # Plot!
                    st.plotly_chart(fig, use_container_width=True)

                # download the results
                st.sidebar.markdown("### Download")

                prefix   = st.sidebar.text_input("Please the prefix name for the results:", "deseq2")
                download = prefix + "_" + "results.zip" ## 下载保存名字

                zip_data = st.sidebar.checkbox("Zip the results", value=st.session_state['zipResults'], on_change=binaryswitch, args = (st.session_state, 'zipResults',))
                if zip_data:

                    #1 zip_directory (str): path to directory  you want to zip 
                    #2 zip_path (str): where you want to save zip file, 需要加上前缀名
                    #3 filename (str): download filename for user who download this
                    create_download_zip(user_dir, "./results/"+prefix, download)
                    ## app重启后删掉相关文件夹
                    #atexit.register(cleanup_tmpdir, user_dir+"_results.zip")

    ## Contact
    showSGR()

if __name__ == "__main__":
    main()