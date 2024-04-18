import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import multipletests
import numpy as np
import os
import subprocess


# Visualize differential expression results
def plot_de_results(results):
    # Adjust p-values for multiple testing
    results['padj']      = multipletests(results['padj'], method='fdr_bh')[1]

    # Calculate -log10 adjusted p-value
    results['log10padj'] = -np.log10(results['padj'] + 1e-100)
    
    # Plot volcano plot
    plt.figure(figsize=(10, 6))
    plt.scatter(results['log2FoldChange'], -1 * results['log10padj'], color='blue', alpha=0.5)
    plt.xlabel('Log2 Fold Change')
    plt.ylabel('-Log10 Adjusted P-value')
    plt.title('Volcano Plot')
    st.pyplot(plt.gcf())

# Main function to run the app
def main():
    st.title("Bulk RNA-Seq Differential Expression Analysis")

    # File upload for RNA-Seq data
    st.subheader("Upload your RNA-Seq data (CSV format)")
    exp_file  = st.file_uploader("Choose a CSV file for gene expression",   type="csv")
    meta_file = st.file_uploader("Choose a CSV file for group comparisons", type="csv")

    if exp_file is not None and meta_file is not None:

        # Load gene data
        data = pd.read_csv(exp_file)
        st.subheader("gene expression (Top 10 rows)")
        st.write(data.head(10))
        data.to_csv("gene.csv", index=False)

        # Load group comparisons
        meta = pd.read_csv(meta_file)
        st.subheader("group comparisons")
        st.write(meta)
        meta.to_csv("meta.csv", index=False)

        ## output file
        out_file = "res.csv"

        # Button to trigger R script execution
        if st.button('Run DESeq2 for comparisons:'):
        # Call the function to run R script
            process1 = subprocess.Popen(["Rscript", "DESeq2.r", "gene.csv", "meta.csv", "res.csv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            result1  = process1.communicate()
            st.write('DESeq2 executed successfully!')

            # Display differential expression results
            results = pd.read_csv("res.csv")
            st.subheader("Differential Expression Results")
            st.write(results)
        
            # Plot differential expression results
            st.subheader("Visualizations")
            plot_de_results(results)



if __name__ == "__main__":
    main()