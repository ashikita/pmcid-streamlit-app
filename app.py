import streamlit as st
import pandas as pd
import requests
import time
import io
from datetime import datetime

# Secrets から読み込み
email = st.secrets["api"]["email"]
tool = st.secrets["api"]["tool"]

# Streamlit UI
st.title("DOI → PMID/PMCID 変換ツール (PMC ID Converter API)")
st.write("TSV形式のDOIリストをアップロードしてください。最大1000件まで対応しています。")

uploaded_file = st.file_uploader("DOIリストファイルをアップロード (TSV形式)", type=["tsv", "txt"])

if uploaded_file:
    st.success("ファイルがアップロードされました。処理を開始します。")
    start_time = datetime.now()

    content = uploaded_file.read().decode("utf-8")
    lines = content.strip().split("\n")
    doi_list = [line.split("\t") for line in lines]
    doi_list = [(int(index), doi.strip()) for index, doi in doi_list]  # DOIをstripで整形

    results = []

    for i in range(0, len(doi_list), 200):
        batch = doi_list[i:i + 200]
        dois = [doi for _, doi in batch]
        ids_param = ",".join(dois)

        url = f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?tool={tool}&email={email}&ids={ids_param}&format=json"
        batch_start = datetime.now()
        response = requests.get(url)
        time.sleep(0.5)

        if response.status_code == 200:
            data = response.json()
            records = {record.get("doi", "").lower(): record for record in data.get("records", [])}
        else:
            records = {}

        for index, doi in batch:
            record = records.get(doi.lower())
            pmid = record.get("pmid", "N/A") if record else "N/A"
            pmcid = record.get("pmcid", "N/A") if record else "N/A"
            results.append((index, doi, pmid, pmcid))

        batch_end = datetime.now()
        elapsed = (batch_end - batch_start).total_seconds()
        st.info(f"{i + len(batch)} 件処理完了（所要時間: {elapsed:.2f}秒）")

    total_elapsed = (datetime.now() - start_time).total_seconds()
    st.success(f"処理完了（全体所要時間: {total_elapsed:.2f}秒）")

    df = pd.DataFrame(results, columns=["index", "doi", "pmid", "pmcid"])
    df["doi"] = df["doi"].str.strip()  # 念のため再度整形
    st.dataframe(df)

    tsv_buffer = io.StringIO()
    df.to_csv(tsv_buffer, sep="\t", index=False)
    tsv_bytes = tsv_buffer.getvalue().encode("utf-8")

    st.download_button(
        label="結果をダウンロード（TSV形式）",
        data=tsv_bytes,
        file_name="pmcid_results.tsv",
        mime="text/tab-separated-values"
    )
