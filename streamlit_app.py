import streamlit as st
import pandas as pd

st.set_page_config(page_title="회전율 낮은 상품 분석기", layout="wide")

st.title("📦 회전율 낮은 상품 분석 앱")
st.write("업로드한 판매 & 재고 데이터를 기반으로 회전율이 낮은 상품을 추출해줍니다.")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드 (상품명, 판매수량, 재고수량 포함)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 필수 컬럼 존재 여부 확인
    required_cols = {"상품명", "판매수량", "재고수량"}
    if not required_cols.issubset(df.columns):
        st.error("❗ CSV 파일에 '상품명', '판매수량', '재고수량' 컬럼이 모두 포함되어 있어야 합니다.")
    else:
        # 회전율 계산
        df["회전율"] = df["판매수량"] / df["재고수량"].replace(0, 1)  # 재고가 0이면 1로 대체

        # 회전율 1 이하 필터링
        low_turnover_df = df[df["회전율"] <= 1].copy()
        low_turnover_df.sort_values(by="회전율", inplace=True)

        st.subheader("📉 회전율 1 이하 상품 목록")
        st.dataframe(low_turnover_df, use_container_width=True)

        # 시각화
        st.subheader("📊 회전율 분포 시각화")
        st.bar_chart(low_turnover_df.set_index("상품명")["회전율"])

        # 다운로드
        st.download_button(
            label="📥 낮은 회전율 상품 리스트 다운로드",
            data=low_turnover_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="low_turnover_items.csv",
            mime="text/csv"
        )
