import pandas as pd
import io

# サンプルデータ（問題の再現）
data = [
    (1, "10.1000/xyz123", "12345678", "PMC123456"),
    (2, "10.1000/abc456\r", "N/A", "N/A"),
    (3, "10.1000/def789", "87654321", "PMC654321")
]

# DataFrameに変換
df = pd.DataFrame(data, columns=["index", "doi", "pmid", "pmcid"])

# TSVとして保存（問題の再現）
tsv_buffer = io.StringIO()
df.to_csv(tsv_buffer, sep="\t", index=False)
output = tsv_buffer.getvalue()

# 出力内容を表示
print("TSV出力内容:\n")
print(output)

# 改善策：DOIの前後の空白や改行を除去
df["doi"] = df["doi"].str.strip()

# 再度TSV出力
tsv_buffer_clean = io.StringIO()
df.to_csv(tsv_buffer_clean, sep="\t", index=False)
clean_output = tsv_buffer_clean.getvalue()

print("\n修正後のTSV出力内容:\n")
print(clean_output)
