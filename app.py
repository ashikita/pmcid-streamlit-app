import streamlit as st
import pandas as pd
import requests
import time
import io
from datetime import datetime

# Streamlit UI
st.title("DOI → PMID/PMCID 変換ツール (PMC ID Converter API)")
st.write("TSV形式のDOIリストをアップロードしてください。最大1000件まで対応しています。")

uploaded_file = st.file_uploader("DOIリストファイルをアップロード (TSV形式)", type=["tsv", "txt"])

if uploaded_file:
    # 処理開始
    st.success("ファイルがアップロードされました。処理を開始します。")
    start_time = datetime.now()

    # DOIリストの読み込み
    content = uploaded_file.read().decode("utf-8")
    lines = content.strip().split("\n")
    doi_list = [line.split("\t") for line in lines]
    doi_list = [(int(index), doi) for index, doi in doi_list]

    # 結果格納用リスト
    results = []

    # バッチ処理
    for i in range(0, len(doi_list), 200):
        batch = doi_list[i:i + 200]
        indices = [str(index) for index, _ in batch]
        dois = [doi for _, doi in batch]
        ids_param = ",".join(dois)

        url = f"https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?tool=ku_library&email=ashikita.takuya.221@m.kyushu-u.ac.jp&ids={ids_param}&format=json"
        batch_start = datetime.now()
        response = requests.get(url)
        time.sleep(0.5)  # 1秒に2件まで

        if response.status_code == 200:
            data = response.json()
            records = {record.get("doi", "").lower(): record for record in data.get("records", [])}
        else:
            records = {}

        for index, doi in batch:
            record = records.get(doi.lower())
            if record:
                pmid = record.get("pmid", "#ERROR#")
                pmcid = record.get("pmcid", "#ERROR#")
            else:
                pmid = "#ERROR#"
                pmcid = "#ERROR#"
            results.append((index, doi, pmid, pmcid))

        batch_end = datetime.now()
        elapsed = (batch_end - batch_start).total_seconds()
        st.info(f"{i + len(batch)} 件処理完了（所要時間: {elapsed:.2f}秒）")

    total_elapsed = (datetime.now() - start_time).total_seconds()
    st.success(f"処理完了（全体所要時間: {total_elapsed:.2f}秒）")

    # DataFrameに変換
    df = pd.DataFrame(results, columns=["index", "doi", "pmid", "pmcid"])
    st.dataframe(df)

    # ダウンロード用TSV作成
    tsv_buffer = io.StringIO()
    df.to_csv(tsv_buffer, sep="\t", index=False)
    tsv_bytes = tsv_buffer.getvalue().encode("utf-8")

    st.download_button(
        label="結果をダウンロード（TSV形式）",
        data=tsv_bytes,
        file_name="pmcid_results.tsv",
        mime="text/tab-separated-values"
    )
