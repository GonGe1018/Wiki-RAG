import os
import datetime
import streamlit as st
from crawler import WikiCrawler
from summarizer import OpenAISummarizer
from rag_pipeline import RAGPipeline

st.title("위키 크롤링 및 요약, RAG 기반 Q&A 시스템")
st.write("URL과 문서 제목을 입력하여 크롤링 및 요약을 수행하고 RAG 파이프라인을 구축합니다.")
st.write("탐색 depth가 클수록 시간이 오래 걸릴 수 있습니다. 빠른 테스트를 원한다면 depth 1을 추천합니다.")
st.write("현재 나무위키만 지원 중입니다.")

if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "pipeline_loaded" not in st.session_state:
    st.session_state["pipeline_loaded"] = False
    st.session_state["pipeline"] = None

st.sidebar.title("설정")
st.sidebar.write("OpenAI API 키를 입력하세요:")
st.session_state["api_key"] = st.sidebar.text_input(
    "API 키 입력", type="password", value=st.session_state["api_key"]
)

st.subheader("1. 크롤링 및 요약")
url = st.text_input("크롤링 시작 URL", "")
document_title = st.text_input("시작 문서 제목", "")
max_depth = st.slider("크롤링 최대 깊이", min_value=1, max_value=5, value=1)

if st.button("크롤링 및 요약 실행"):
    if not st.session_state["api_key"]:
        st.error("OpenAI API 키를 입력하세요.")
    elif not url.strip():
        st.error("크롤링 시작 URL을 입력하세요.")
    elif not document_title.strip():
        st.error("시작 문서 제목을 입력하세요.")
    else:
        crawler = WikiCrawler()
        summarizer = OpenAISummarizer(api_key=st.session_state["api_key"])
        try:
            with st.spinner(f"크롤링 및 요약 중: {url}"):
                res = crawler.bfs_crawl(
                    url=url,
                    document_title=document_title,
                    max_depth=max_depth
                )

                current_time = datetime.datetime.now()
                dir_name = current_time.strftime("%Y%m%d%H%M%S")
                summarizer.save_results(res, dir_name)

                st.session_state["dir_name"] = dir_name

                st.success(f"크롤링 및 요약 완료! 결과는 '{dir_name}' 폴더에 저장되었습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
        finally:
            crawler.close()

st.subheader("2. RAG 파이프라인 구축")

dir_name = st.text_input(
    "크롤링 및 요약 결과 폴더 경로 입력 (예: 20231115120000)",
    value=st.session_state.get("dir_name", "")
)

index_dir = st.text_input(
    "RAG 파이프라인 인덱스 저장 경로 (예: faiss_index)", value="faiss_index"
)

if st.button("RAG 파이프라인 구축"):
    if not dir_name.strip():
        st.error("크롤링 및 요약 결과 폴더 경로를 입력하세요.")
    elif not os.path.exists(dir_name):
        st.error(f"'{dir_name}' 폴더가 존재하지 않습니다. 올바른 경로를 입력하세요.")
    else:
        if not os.path.exists(index_dir):
            os.makedirs(index_dir, exist_ok=True)

        try:
            with st.spinner("RAG 파이프라인 구축 중..."):
                res_list = []
                for root, _, files in os.walk(f"{dir_name}/output_summarized"):
                    for file in files:
                        if file.endswith(".txt"):
                            file_path = os.path.join(root, file)
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            title = os.path.splitext(file)[0]
                            res_list.append((title, content))

                if res_list:
                    rag_pipeline = RAGPipeline(index_dir=index_dir, openai_api_key=st.session_state["api_key"])
                    rag_pipeline.prepare_data(res_list)
                    st.success(f"RAG 파이프라인이 '{index_dir}'에 구축되었습니다.")
                else:
                    st.error("크롤링 결과에서 유효한 데이터를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")

st.subheader("3. RAG 파이프라인 로드 및 질문")
available_indices = [d for d in os.listdir(".") if os.path.isdir(d) and "faiss_index" in d]
selected_index = st.selectbox("사용할 파이프라인 선택", options=available_indices)

if st.button("RAG 파이프라인 로드"):
    try:
        with st.spinner(f"RAG 파이프라인 로드 중: {selected_index}"):
            rag_pipeline = RAGPipeline(index_dir=selected_index, openai_api_key=st.session_state["api_key"])
            st.session_state["pipeline"] = rag_pipeline.load_pipeline()
            st.session_state["pipeline_loaded"] = True
            st.success(f"RAG 파이프라인 '{selected_index}'이 로드되었습니다.")
    except FileNotFoundError:
        st.error("선택한 파이프라인이 존재하지 않습니다. 먼저 파이프라인을 구축하세요.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

if st.session_state["pipeline_loaded"]:
    pipeline = st.session_state["pipeline"]
    user_query = st.text_input("질문을 입력하세요:", "")
    if st.button("질문하기") and user_query.strip():
        with st.spinner("답변 생성 중..."):
            try:
                result = pipeline({"query": user_query})
                st.subheader("전체 결과")
                st.write(result)
                st.subheader("답변")
                st.write(result.get("result", "결과 없음"))
                st.subheader("출처 문서")
                for doc in result.get("source_documents", []):
                    st.write(f"**{doc.metadata.get('title', '제목 없음')}**")
                    st.write(doc.page_content[:500])
            except Exception as e:
                st.error(f"오류 발생: {e}")
