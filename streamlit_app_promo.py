
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="6개월 이상 장기 재고 처리 앱", layout="wide")
st.title("📦 장기 재고 판매 촉진 및 반송 요청 자동화 앱")

st.write("업로드한 데이터를 바탕으로 재고 보관기간이 6개월(180일) 이상인 상품을 자동 분류합니다.")

uploaded_file = st.file_uploader("CSV 파일 업로드 (상품명, 입고일, 재고수량, 판매수량, 마진율 포함)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    required_cols = {"상품명", "입고일", "재고수량", "판매수량", "마진율"}
    if not required_cols.issubset(df.columns):
        st.error("❗ CSV에 '상품명', '입고일', '재고수량', '판매수량', '마진율' 컬럼이 모두 포함되어야 합니다.")
    else:
        # 날짜 처리
        df["입고일"] = pd.to_datetime(df["입고일"], errors='coerce')
        df["보관일수"] = (datetime.today() - df["입고일"]).dt.days

        # 회전율 계산
        df["회전율"] = df["판매수량"] / df["재고수량"].replace(0, 1)

        # 장기 보관 & 회전율 낮은 상품 필터링
        long_stock_df = df[(df["보관일수"] >= 180) & (df["회전율"] <= 1)]

        if long_stock_df.empty:
            st.success("✅ 6개월 이상 보관된 저회전 상품이 없습니다!")
        else:
            st.subheader("📊 분류 결과")
            # 마진율 기준 분류
            promo_df = long_stock_df[long_stock_df["마진율"] >= 0.3]
            return_df = long_stock_df[long_stock_df["마진율"] < 0.3]

            tab1, tab2 = st.tabs(["🟢 프로모션 제안 대상", "🔴 반송 요청 대상"])

            with tab1:
                st.write(f"총 {len(promo_df)}개 상품")
                st.dataframe(promo_df, use_container_width=True)
                st.download_button(
                    "📥 프로모션 대상 다운로드",
                    promo_df.to_csv(index=False).encode("utf-8-sig"),
                    "promotion_targets.csv",
                    "text/csv"
                )

                st.subheader("✉️ 프로모션 제안 메일 문구")
                st.code(
                    f"""안녕하세요,
귀사에서 납품한 일부 상품은 현재 장기 보관 중이며 마진율이 높아 기획전 대상 상품으로 제안드립니다.

총 {len(promo_df)}개 상품이 대상이며, 프로모션 참여 여부 회신 부탁드립니다.

감사합니다."""
                )

            with tab2:
                st.write(f"총 {len(return_df)}개 상품")
                st.dataframe(return_df, use_container_width=True)
                st.download_button(
                    "📥 반송 요청 대상 다운로드",
                    return_df.to_csv(index=False).encode("utf-8-sig"),
                    "return_requests.csv",
                    "text/csv"
                )

                st.subheader("✉️ 반송 요청 메일 문구")
                st.code(
                    f"""안녕하세요,
귀사에서 납품한 일부 상품이 장기 보관(6개월 이상) 상태이며, 판매 회전율이 낮은 상황입니다.

총 {len(return_df)}개 상품에 대해 반송 또는 처리 협의를 요청드립니다.

감사합니다."""
                )
