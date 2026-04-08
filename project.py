import streamlit as st
import pandas as pd
import re
import google.generativeai as genai
import json
import plotly.express as px

# ==========================================
# 🛑 核心配置区
# ==========================================
# ⚠️Google API Key (以 AIza 开头)写·
API_KEY = st.secrets["GEMINI_API_KEY"] 

# 页面基础设置
st.set_page_config(page_title="ProfitLens AI", page_icon="📈", layout="wide")

# ==========================================
# 🌐 国际化字典 (i18n Dictionary)
# ==========================================
LANG = {
    "中文": {
        "title": "📈 ProfitLens AI - 社交媒体商业变现中枢",
        "console": "🎛️ 系统控制台",
        "mode_select": "🔮 分析模式",
        "mode_1": "🎯 单文案深度审计",
        "mode_2": "⚔️ A/B 棋盘推演",
        "niche": "选择赛道:",
        "cost": "预估制作/投流成本 $:",
        "btn_1": "⚡️ 开始单篇深度审计",
        "btn_2": "⚡️ 开始 A/B 深度推演",
        "ai_lang": "中文 (Chinese)",
        "input_single": "在此粘贴你的单篇文案 (Max 2000字):",
        "input_a": "⚪️ 文案 A (如: 激进带货版):",
        "input_b": "⚫️ 文案 B (如: 保守干货版):",
        "processing": "🔍 系统正在调用原生 AI 大脑进行深度计算与图表绘制...",
        "success": "✅ 商业分析与财务审计完成！",
        "score": "最终获利潜力分",
        "value": "预估广告价值",
        "profit": "预估净利润",
        "analysis_matrix": "💼 多维商业决策矩阵 (可视化图表)",
        "diag_report": "🧠 AI 商业总监深度诊断报告",
        "winner_a": "🏆 核心财务对决：⚪️ 文案 A 胜出",
        "winner_b": "🏆 核心财务对决：⚫️ 文案 B 胜出",
        "winner_tie": "🤝 核心财务对决：战平"
    },
    "English": {
        "title": "📈 ProfitLens AI - Social Media Monetization Hub",
        "console": "🎛️ System Console",
        "mode_select": "🔮 Select Mode",
        "mode_1": "🎯 Single Post Audit",
        "mode_2": "⚔️ A/B Testing Engine",
        "niche": "Select Niche:",
        "cost": "Est. Production Cost $:",
        "btn_1": "⚡️ Run Single Post Audit",
        "btn_2": "⚡️ Run A/B Testing",
        "ai_lang": "English",
        "input_single": "Paste your post text here (Max 2000 chars):",
        "input_a": "⚪️ Text A (e.g., Aggressive Sales):",
        "input_b": "⚫️ Text B (e.g., Value-Driven):",
        "processing": "🔍 AI is processing and plotting charts...",
        "success": "✅ Analysis completed!",
        "score": "Potential Score",
        "value": "Est. Ad Value",
        "profit": "Est. Net Profit",
        "analysis_matrix": "💼 Business Decision Matrix (Visual Charts)",
        "diag_report": "🧠 AI Director's Post-Match Review",
        "winner_a": "🏆 Core Duel: ⚪️ Text A Wins",
        "winner_b": "🏆 Core Duel: ⚫️ Text B Wins",
        "winner_tie": "🤝 Core Duel: Tie"
    },
    "Français": {
        "title": "📈 ProfitLens AI - Hub de Monétisation Sociale",
        "console": "🎛️ Console Système",
        "mode_select": "🔮 Mode d'Analyse",
        "mode_1": "🎯 Audit de Post Unique",
        "mode_2": "⚔️ Moteur de Test A/B",
        "niche": "Sélectionner la Niche:",
        "cost": "Coût de Production Est. $:",
        "btn_1": "⚡️ Lancer l'Audit Unique",
        "btn_2": "⚡️ Lancer le Test A/B",
        "ai_lang": "Français (French)",
        "input_single": "Collez votre texte ici (Max 2000 carac.):",
        "input_a": "⚪️ Texte A (ex: Vente Agressive):",
        "input_b": "⚫️ Texte B (ex: Contenu de Valeur):",
        "processing": "🔍 Le système traite et trace les graphiques...",
        "success": "✅ Analyse commerciale terminée !",
        "score": "Score de Potentiel",
        "value": "Valeur Pub Est.",
        "profit": "Bénéfice Net Est.",
        "analysis_matrix": "💼 Matrice de Décision d'Affaires (Graphiques Visuels)",
        "diag_report": "🧠 Revue du Directeur AI",
        "winner_a": "🏆 Duel Principal: ⚪️ Texte A Gagne",
        "winner_b": "🏆 Duel Principal: ⚫️ Texte B Gagne",
        "winner_tie": "🤝 Duel Principal: Égalité"
    }
}

# 尝试读取本地 Excel 词库
try:
    df = pd.read_excel("keywords.xlsx")
except:
    df = pd.DataFrame()

# ==========================================
# ⚙️ 左侧：全局控制台与多语言切换
# ==========================================
with st.sidebar:
    selected_lang = st.sidebar.selectbox("Language / Langue / 语言", ['English', 'Français', '中文'], index=0)
    t = LANG[selected_lang]
    st.markdown("---")
    
    st.header(t["console"])
    app_mode = st.radio(t["mode_select"], [t["mode_1"], t["mode_2"]])
    st.markdown("---")
    
    niche = st.selectbox(t["niche"], ["Finance", "Tech", "Beauty", "Lifestyle", "Gaming"])
    content_cost = st.number_input(t["cost"], min_value=0, max_value=1000, value=20, step=5)

st.title(t["title"])
st.markdown("---")

# ==========================================
# 🎯 模式一：单文案深度审计 (带单轨图表)
# ==========================================
if app_mode == t["mode_1"]:
    user_text = st.text_area(t["input_single"], height=200)
    analyze_btn = st.button(t["btn_1"], use_container_width=True)
    
    if analyze_btn and user_text.strip() != "":
        with st.spinner(t["processing"]):
            # 1. Python 扫描关键词并计算底盘数据
            found_keywords = [str(row.iloc[1]) for idx, row in df.iterrows() if str(row.iloc[1]) in user_text and str(row.iloc[1]) != "nan"] if not df.empty else []
            base_score = min(100, 50 + len(found_keywords) * 10)
            base_est_min = len(found_keywords) * 15
            base_est_max = len(found_keywords) * 25 + 20

            # 2. 调用 AI 大脑获取参数和图表数据包 (🆕 融入了投资成本考量)
            try:
                genai.configure(api_key=API_KEY)
                prompt = f"""
                You are a top MCN business consultant. Niche: {niche}. Text: "{user_text}". Found keywords: {found_keywords}.
                Cost constraint: The estimated production/ad cost is ${content_cost}. 
                Task 1: Sentiment Multiplier. Strong positive=1.2, Neutral=1.0, Slight negative=0.5, Strong negative (complaints)=0.0.
                Task 2: MUST output EXACTLY this format in the first line: [情绪乘数:X.X]
                Task 3: MUST output a JSON object in a markdown block for chart rendering. Format strictly like this (Added LifeCycle dimension):
                ```json
                {{"Profitability": 85, "Scalability": 70, "LongTerm": 90, "Engagement": 80, "LifeCycle": 88}}
                ```
                Task 4: Provide diagnosis and 2 suggestions. You MUST critically evaluate if the text quality and potential ROI justify the ${content_cost} investment risk. 
                NEW: You MUST evaluate the "Data & Lifecycle" of the content. Is it a short-lived trend or does it have long-tail SEO search value?
                Task 5: HIGHLIGHT important keywords, data points, and core concepts in your text using Streamlit's Markdown color syntax. Examples: :red[High Risk], :blue[Monetization Strategy], :green[High ROI], :orange[Key Metric], :violet[Audience].
                🛑 CRITICAL: The diagnosis text MUST be entirely in {t['ai_lang']}.
                """
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                ai_text = model.generate_content(prompt).text
                
                # 3. Python 正则抓取与数据清洗
                mult_match = re.search(r'\[情绪乘数:([0-9\.]+)\]', ai_text)
                json_match = re.search(r'```json\n(.*?)\n```', ai_text, re.DOTALL)
                
                multiplier = float(mult_match.group(1)) if mult_match else 1.0
                final_score = min(100, int(base_score * multiplier))
                final_est_min = int(base_est_min * multiplier)
                final_est_max = int(base_est_max * multiplier)
                
                chart_df = pd.DataFrame()
                clean_ai_text = ai_text
                
                if json_match:
                    try:
                        chart_data_dict = json.loads(json_match.group(1))
                        chart_df = pd.DataFrame(list(chart_data_dict.items()), columns=['Dimension', 'Score'])
                        
                        clean_ai_text = re.sub(r'```json\n.*?\n```', '', ai_text, flags=re.DOTALL)
                        clean_ai_text = re.sub(r'\[情绪乘数:[0-9\.]+\]\n*', '', clean_ai_text)
                    except Exception as e:
                        pass 

            except Exception as e:
                clean_ai_text = f"⚠️ AI Connection Error: {e}"
                chart_df, multiplier = pd.DataFrame(), 1.0
                final_score, final_est_min, final_est_max = base_score, base_est_min, base_est_max

            # 财务核算
            net_profit = ((final_est_min + final_est_max) / 2) - content_cost
            roi_str = f"{(net_profit / content_cost) * 100:.1f}%" if content_cost > 0 else "∞"

        # 4. 界面渲染
        st.success(t["success"])
        col1, col2, col3 = st.columns(3)
        col1.metric(t["score"], f"{final_score} / 100")
        col2.metric(t["value"], "$0" if multiplier == 0.0 else f"${final_est_min} - ${final_est_max}")
        col3.metric(t["profit"], f"${net_profit:.1f}", f"ROI: {roi_str}")
        st.markdown("---")
        
        # 图表渲染区 
        st.subheader(t["analysis_matrix"])
        if not chart_df.empty:
            fig = px.bar(chart_df, x='Dimension', y='Score', text='Score', color_discrete_sequence=['#4CAF50'])
            fig.update_layout(
                xaxis_tickangle=0, 
                xaxis_title=None,
                yaxis_title="Score"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        st.subheader(t["diag_report"])
        st.write(clean_ai_text)

# ==========================================
# ⚔️ 模式二：A/B 棋盘推演 (带双轨可视化比对)
# ==========================================
elif app_mode == t["mode_2"]:
    col_input_a, col_input_b = st.columns(2)
    with col_input_a: text_a = st.text_area(t["input_a"], height=200)
    with col_input_b: text_b = st.text_area(t["input_b"], height=200)
    
    analyze_btn = st.button(t["btn_2"], use_container_width=True)
    
    if analyze_btn and text_a.strip() != "" and text_b.strip() != "":
        with st.spinner(t["processing"]):
            # 1. Python 双侧扫描底盘数据
            def scan_keywords(text):
                return [str(row.iloc[1]) for idx, row in df.iterrows() if str(row.iloc[1]) in text and str(row.iloc[1]) != "nan"] if not df.empty else []

            kw_a, kw_b = scan_keywords(text_a), scan_keywords(text_b)
            base_est_a, base_est_b = len(kw_a) * 20 + 10, len(kw_b) * 20 + 10

            # 2. 调用 AI 大脑进行对比并输出比对 JSON (🆕 融入了双边成本考量)
            try:
                genai.configure(api_key=API_KEY)
                prompt = f"""
                You are a top business analyst. A/B Testing. Niche: {niche}.
                Cost constraint: The estimated production/ad cost for EACH plan is ${content_cost}.
                【Text A】: "{text_a}"
                【Text B】: "{text_b}"
                
                Task 1: Output EXACTLY this format in the first line: [A_乘数:X.X, B_乘数:Y.Y] (0.0 to 1.2)
                Task 2: Output a JSON object in a markdown block for dual-chart rendering. Format strictly:
                ```json
                {{"Dimension": ["Profitability", "Scalability", "LongTerm", "Engagement", "LifeCycle"], "Text_A": [80, 60, 70, 85, 90], "Text_B": [60, 80, 90, 75, 65]}}
                ```
                Task 3: Detailed comparison report. You MUST critically evaluate which text offers a more secure or aggressive return on the ${content_cost} investment, and advise if either plan is at risk of a negative ROI. Compare the "Data & Lifecycle" between the two texts.
                
                Task 4: VISUAL HIGHLIGHTING (CRITICAL). You MUST use Streamlit's Markdown color syntax to highlight key information in your report. 
                Strict Color Code Rules:
                - Use :red[text] for risks, negative ROI, disadvantages, or high costs.
                - Use :green[text] for winners, positive ROI, competitive advantages, or profit.
                - Use :blue[text] for specific data metrics, dimensions (e.g., Engagement, LifeCycle), or objective facts.
                - Use :orange[text] for strategic advice, core concepts, or actionable insights.
                Example format: ":green[方案 A] 在 :blue[互动率] 上表现更好，但存在 :red[极高的成本风险]，建议采用 :orange[长尾搜索策略]。"
                
                🛑 CRITICAL: Write the comparison report entirely in {t['ai_lang']}.
                """
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                ai_text = model.generate_content(prompt).text
                
                # 3. 数据解析
                mult_match = re.search(r'\[A_乘数:([0-9\.]+), B_乘数:([0-9\.]+)\]', ai_text)
                mult_a = float(mult_match.group(1)) if mult_match else 1.0
                mult_b = float(mult_match.group(2)) if mult_match else 1.0
                
                json_match = re.search(r'```json\n(.*?)\n```', ai_text, re.DOTALL)
                comparison_df = pd.DataFrame()
                clean_ai_text = ai_text
                
                if json_match:
                    try:
                        chart_dict = json.loads(json_match.group(1))
                        comparison_df = pd.DataFrame(chart_dict) 
                        clean_ai_text = re.sub(r'```json\n.*?\n```', '', ai_text, flags=re.DOTALL)
                        clean_ai_text = re.sub(r'\[A_乘数:.*?\]\n*', '', clean_ai_text)
                    except Exception as e:
                        pass
                        
                profit_a = (base_est_a * mult_a) - content_cost
                profit_b = (base_est_b * mult_b) - content_cost

            except Exception as e:
                clean_ai_text = f"⚠️ AI Error: {e}"
                comparison_df = pd.DataFrame()
                profit_a, profit_b = base_est_a - content_cost, base_est_b - content_cost

        # 4. 界面渲染对决结果
        st.success(t["success"])
        winner = t["winner_a"] if profit_a > profit_b else t["winner_b"] if profit_b > profit_a else t["winner_tie"]
        st.subheader(winner)
        
        col_res_a, col_res_b = st.columns(2)
        with col_res_a: 
            st.info("⚪️ **Text A**")
            st.metric(t["profit"], f"${profit_a:.1f}")
        with col_res_b: 
            st.success("⚫️ **Text B**")
            st.metric(t["profit"], f"${profit_b:.1f}")
            
        st.markdown("---")
        
        # 图表对决展示区 
        st.subheader(t["analysis_matrix"])
        if not comparison_df.empty:
            df_melted = comparison_df.melt(id_vars="Dimension", var_name="Plan", value_name="Score")
            
            fig_ab = px.bar(
                df_melted, 
                x="Dimension", 
                y="Score", 
                color="Plan", 
                barmode="group", 
                text="Score",
                color_discrete_map={"Text_A": "#A0C4FF", "Text_B": "#FFADAD"} 
            )
            fig_ab.update_layout(
                xaxis_tickangle=0, 
                xaxis_title=None,
                yaxis_title="Score",
                legend_title="方案"
            )
            st.plotly_chart(fig_ab, use_container_width=True)
            
        st.subheader(t["diag_report"])
        st.write(clean_ai_text)
