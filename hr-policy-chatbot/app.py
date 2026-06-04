# app.py
import streamlit as st
from rag_chain import ask_question, load_vectorstore
from confidence import confidence_label
from escalation import should_escalate, escalate_to_hr
from audit_log import init_db, log_query

st.set_page_config(
    page_title='HR Policy Assistant',
    page_icon='📋',
    layout='centered'
)

init_db()

@st.cache_resource
def get_vectorstore():
    return load_vectorstore()

vectorstore = get_vectorstore()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ── ONBOARDING SCREEN ────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title('📋 HR Policy Assistant')
    st.markdown('**Welcome!** Please enter your details to continue.')
    st.markdown('---')

    with st.form('login_form'):
        name   = st.text_input('Full Name', placeholder='e.g. Ravi Kumar')
        emp_id = st.text_input('Employee ID', placeholder='e.g. EMP1042')
        submitted = st.form_submit_button('Start Chatting')

        if submitted:
            if name.strip() and emp_id.strip():
                st.session_state.employee_name = name.strip()
                st.session_state.employee_id   = emp_id.strip()
                st.session_state.logged_in     = True
                st.rerun()
            else:
                st.error('Please fill in both fields.')

    st.markdown('---')
    st.markdown('**💡 People commonly ask:**')
    for q in [
        'How many casual leaves am I entitled to?',
        'What is the work from home policy?',
        'What is the reimbursement process for business travel?',
        'How do I apply for maternity or paternity leave?',
    ]:
        st.markdown(f'- {q}')

# ── CHAT SCREEN ──────────────────────────────────────────────────────────────
else:
    st.title('📋 HR Policy Assistant')
    st.markdown(
        f'Hello **{st.session_state.employee_name}** '
        f'({st.session_state.employee_id}) — '
        'Ask me anything about company HR policies!'
    )
    st.markdown('---')

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            if msg['role'] == 'assistant' and 'confidence' in msg:
                label, color = confidence_label(msg['confidence'])
                st.markdown(
                    f'<span style="background:{color};color:white;'
                    f'padding:3px 10px;border-radius:12px;font-size:13px;">'
                    f'📊 {label}: {msg["confidence"]}%</span>',
                    unsafe_allow_html=True
                )
                if msg.get('sources'):
                    with st.expander('📄 Sources'):
                        for src in msg['sources']:
                            st.markdown(f'- {src}')

    # Chat input
    if question := st.chat_input('Ask your HR question here...'):
        st.session_state.messages.append(
            {'role': 'user', 'content': question}
        )
        with st.chat_message('user'):
            st.markdown(question)

        with st.chat_message('assistant'):
            with st.spinner('Searching HR policies...'):
                result = ask_question(question, vectorstore)

            answer     = result['answer']
            confidence = result['confidence']
            sources    = result['sources']

            st.markdown(answer)

            label, color = confidence_label(confidence)
            st.markdown(
                f'<span style="background:{color};color:white;'
                f'padding:3px 10px;border-radius:12px;font-size:13px;">'
                f'📊 {label}: {confidence}%</span>',
                unsafe_allow_html=True
            )

            if sources:
                with st.expander('📄 Sources'):
                    for src in sources:
                        st.markdown(f'- {src}')

            escalated = False
            if should_escalate(confidence):
                escalated = escalate_to_hr(
                    st.session_state.employee_name,
                    st.session_state.employee_id,
                    question, confidence
                )
                if escalated:
                    st.warning(
                        '⚠️ Confidence is low. HR has been automatically '
                        'notified and will follow up with you shortly.'
                    )

        st.session_state.messages.append({
            'role': 'assistant',
            'content': answer,
            'confidence': confidence,
            'sources': sources
        })

        log_query(
            st.session_state.employee_name,
            st.session_state.employee_id,
            question, answer, confidence, escalated
        )
        