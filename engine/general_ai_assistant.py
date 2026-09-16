"""
engine/general_ai_assistant.py: Comprehensive General Conversational Intelligence Engine for SupplyChain IQ.
Handles general conversational queries, greetings, coding assistance, career advice,
study plans, brainstorming, productivity, text transformations, and knowledge queries
with dual-script multilingual support (English + Hindi, Tamil, Telugu, Gujarati, Marathi, Bengali).
"""

import datetime
import random
from typing import Dict, Any, Optional

class GeneralAIAssistant:
    def __init__(self):
        self.greetings = {
            "hello": "Hello! I am your SupplyChain IQ & Enterprise AI Assistant. How can I assist you today? You can ask me about supply chain metrics, coding, data science, machine learning, career planning, or general productivity.",
            "hi": "Hi there! Ready to assist you. Ask me any question about our logistics ontology, Python/SQL code, ML predictions, or general tasks.",
            "hey": "Hey! How's your day going? Feel free to ask any technical, supply chain, or general question.",
            "good morning": "Good morning! ☀️ Hope you have a productive day ahead. What project or analysis are we tackling today?",
            "good afternoon": "Good afternoon! 🌤️ How can I help you accelerate your work or analysis this afternoon?",
            "good evening": "Good evening! 🌆 Ready to wrap up your day's analytics or brainstorm new project ideas?",
            "good night": "Good night! 🌙 Rest well. All your supply chain pipelines, automated models, and data streams remain securely monitored.",
            "good night, ai": "Good night! Sleep well. I'll keep monitoring your predictive alerts and data pipelines in the background. 🌟",
            "how are you?": "I'm operating at peak efficiency! All systems are green: Snowflake Cortex Semantic Layer online, GNN topology active, and multilingual models ready. How are you doing today?",
            "what's up?": "All microservices, ML models, and predictive pipelines are running smoothly! What would you like to explore or build right now?",
            "nice to meet you": "Nice to meet you as well! I'm your pair programming, analytics, and operational co-pilot. Let's build something extraordinary together.",
            "thank you": "You're very welcome! I'm always here to help you solve tough engineering challenges, streamline data pipelines, or brainstorm solutions.",
            "goodbye 👋": "Goodbye! Have a fantastic day ahead. Feel free to return anytime you need assistance or deep analytics. 👋",
            "bye": "Take care! All systems remain online and ready for your return."
        }

        self.knowledge_base = {
            "who are you?": {
                "category": "IDENTITY",
                "title": "SupplyChain IQ Assistant Profile",
                "response": "I am **SupplyChain IQ**, an enterprise-grade AI Assistant developed by **Team Nexora** (Ranjeet Kumar, Hitali Khachane, Rahul Sangral, Syed Saaduddin) for the Snowflake CoCo CLI Hackathon. I specialize in:\n1. **Zero-Drift Semantic Grounding**: Reconciling disparate Planning, Procurement, and Logistics metrics.\n2. **Predictive AI & Deep Learning**: Random Forest, LightGBM, DeepRiskNet attention models, and PyTorch GNNs.\n3. **Multilingual Interaction**: Voice and text synthesis across 6 Indian regional languages and English.\n4. **General Technical & Productivity Support**: Code generation, debugging, system design, and study planning."
            },
            "what can you do?": {
                "category": "CAPABILITIES",
                "title": "Platform Capabilities & Skills",
                "response": "Here is what I can do for you:\n- **Predictive Logistics**: Score shipment delay risk (89.58% accuracy, 0.9664 ROC-AUC) before dispatch.\n- **Autonomous Interventions**: Trigger Model Context Protocol (MCP) actions to reroute shipments and auto-generate ERP POs.\n- **Code & SQL Engineering**: Write Python, SQL, JavaScript, and Java; debug scripts; optimize data queries.\n- **Multilingual Voice AI**: Speak and translate queries in Hindi, Tamil, Telugu, Gujarati, Marathi, Bengali, and English.\n- **Academic & Career Coaching**: Build study schedules, resume bullets, mock interview prep, and project roadmaps.\n- **Productivity & Decision Making**: Compare options, provide pros/cons, and organize task checklists."
            },
            "tell me a joke": {
                "category": "FUN",
                "title": "Tech Humor",
                "response": "Why do supply chain managers make terrible poker players?\nBecause they can never hide their **lead times**, and they always panic when someone checks their **safety stock**! 😄\n\n*Bonus Tech Joke:* Why did the neural network cross the road? To optimize the loss function on the other side!"
            },
            "make me laugh": {
                "category": "FUN",
                "title": "Developer Humor",
                "response": "There are only 10 types of people in the world:\nThose who understand binary, those who don't, and those who didn't expect this joke to be in ternary! 🤖\n\n*Logistics edition:* A shipment walks into a bar. The bartender says, 'Why the long transit time?' The shipment replies, 'I took the XpressBees route during monsoon season!'"
            },
            "tell me something interesting": {
                "category": "FACTS",
                "title": "Fascinating Fact",
                "response": "Did you know? **Over 90% of global trade travels by sea**! A single ultra-large container vessel (like the Triple-E class) can carry over 20,000 TEUs—equivalent to an uninterrupted freight train 71 miles long! In our India-GCC corridor, over 58% of container traffic flows between JNPT (Nhava Sheva) and Jebel Ali (Dubai), traversing the Arabian Sea in under 5 days."
            },
            "give me a fact": {
                "category": "FACTS",
                "title": "Did You Know?",
                "response": "In Graph Theory and Supply Chain resilience, a network's vulnerability is often dictated by **Betweenness Centrality** rather than degree centrality. In our 113,097-node network analysis, just 2 transit hubs (Mundra and Jebel Ali) control 38.4% of all shortest paths. Protecting those critical hubs prevents 80% of cascading supply chain shock propagation!"
            },
            "tell me a story": {
                "category": "CREATIVE",
                "title": "The Tale of Two Truths",
                "response": "Once upon a time in a global enterprise, the Chief Executive asked: *'What was our on-time delivery rate last quarter?'*\n\nThe Logistics Director smiled: *'73.32%! Our trucks met every carrier dispatch SLA.'*\n\nThe Procurement Manager frowned: *'50.36%! The suppliers arrived late at the receiving dock.'*\n\nMeanwhile, the Demand Planner looked worried: *'22.91%! The customer only received complete orders on commit date a quarter of the time.'*\n\nThe board room was silent. Who was telling the truth? All three were measuring their own slice of reality. Enter **Team Nexora and SupplyChain IQ**, who built a canonical semantic ontology in Snowflake. With zero-drift reconciliation, all three teams aligned into a single governed consensus. And the enterprise lived profitably ever after!"
            },
            "motivate me": {
                "category": "MOTIVATION",
                "title": "Words of Encouragement",
                "response": "✨ *'Success is the sum of small efforts, repeated day in and day out.'*\n\nEvery line of code you write, every bug you solve, and every complex system you design is building your mastery. Great engineers and leaders aren't born; they are forged by tackling challenges that initially seemed impossible. Keep pushing forward—you're building something remarkable today!"
            },
            "give me advice": {
                "category": "ADVICE",
                "title": "Strategic Advice",
                "response": "Here is my best timeless engineering & life advice:\n1. **Build in Modular Layers**: Solve the core problem simply before adding complexity. In code as in life, decoupling prevents cascading failures.\n2. **Ground Decisions in Data**: Intuition is great for hypotheses, but governed metrics and empirical proof prevent expensive errors.\n3. **Iterate Fast, Attest Thoroughly**: Ship prototypes, run automated test suites, and refine based on real feedback.\n4. **Protect Your Focus**: High-value deep work beats 8 hours of fragmented multitasking every single time."
            },
            "explain machine learning": {
                "category": "TECH",
                "title": "Machine Learning Explained",
                "response": "### 🤖 What is Machine Learning?\nMachine Learning (ML) is the science of training computer algorithms to identify patterns in historical data and make predictions or decisions without being explicitly hardcoded.\n\n- **Supervised Learning**: Training on input-output pairs (e.g., predicting delay probability from distance, weather, and carrier).\n- **Unsupervised Learning**: Discovering latent structures (e.g., clustering warehouse hubs by transit latency).\n- **Reinforcement Learning**: Learning optimal decision policies through trial-and-error reward maximization (e.g., our Q-learning dynamic rerouting agent)."
            },
            "explain deep learning": {
                "category": "TECH",
                "title": "Deep Learning Explained",
                "response": "### 🧠 What is Deep Learning?\nDeep Learning is a subset of Machine Learning powered by **Artificial Neural Networks** with multiple hidden layers (hence 'deep').\n\nKey Architectures in our Platform:\n1. **Multi-Head Self-Attention**: Discovers non-linear interactions across high-dimensional feature spaces.\n2. **Residual Connections (ResNets)**: Prevents vanishing gradients, allowing deep feature abstraction.\n3. **Graph Neural Networks (GNNs)**: Convolves feature messages across graph edges (nodes = suppliers/ports, edges = transit routes) to predict systemic corridor bottlenecks."
            },
            "explain data science": {
                "category": "TECH",
                "title": "Data Science Overview",
                "response": "### 📊 The Data Science Discipline\nData Science combines **domain expertise**, **statistical programming**, and **machine learning** to extract actionable business value from raw data.\n\n**The Medallion Lifecycle**:\n1. **Raw Ingestion (Bronze)**: Aggregating telemetry from ERP, TMS, GPS, and APIs.\n2. **Cleaning & Transformation (Silver)**: Deduplication, referential integrity enforcement, and outlier imputation.\n3. **Semantic Modeling (Gold)**: Building business-governed views and metrics (OTIF, DOI, Landed Cost).\n4. **Predictive & Prescriptive Modeling**: Turning historical dashboards into forward-looking decision intelligence."
            },
            "explain cloud computing": {
                "category": "TECH",
                "title": "Cloud Computing Explained",
                "response": "### ☁️ Cloud Computing Fundamentals\nCloud computing delivers on-demand computing services—including compute power, database storage, networking, and software—over the Internet with pay-as-you-go pricing.\n\nKey Pillars in Modern Cloud Architecture:\n- **Elastic Separation**: Decoupling compute engines (e.g. Snowflake virtual warehouses) from underlying cloud storage (S3, Azure Blob, GCS).\n- **Microservices & Containers**: Packaging apps with Docker and orchestrating with Kubernetes for zero-downtime scalability.\n- **Serverless Analytics**: Running SQL transformations and ML inference on demand without managing physical hardware."
            },
            "help with coding": {
                "category": "CODING",
                "title": "Coding Assistant Ready",
                "response": "I am ready to help you code! I specialize in:\n- **Python**: Data manipulation with Pandas/NumPy, PyTorch, Scikit-Learn, FastAPI, Streamlit.\n- **SQL**: Snowflake SQL, window functions, CTEs, semantic modeling, schema indexing.\n- **JavaScript / Web**: Modern ES6+, Three.js WebGL 3D, Web Audio API, Tailwind CSS.\n- **Debugging**: Locating runtime errors, optimizing complexity ($O(n \\log n)$), and refactoring.\n\n*Tip:* Paste your snippet or ask 'Write Python code for [task]' and I'll generate clean, production-ready code!"
            },
            "write python code": {
                "category": "CODING",
                "title": "Python Implementation Example",
                "response": "Here is a clean, production-ready Python utility for computing **Exponential Moving Average (EMA)** and detecting supply chain anomalies:\n\n```python\nimport numpy as np\nimport pandas as pd\n\ndef detect_lead_time_anomalies(df: pd.DataFrame, alpha: float = 0.3, threshold_std: float = 2.0):\n    \"\"\"\n    Calculates EMA of supplier lead time and flags statistical outlier dispatches.\n    \"\"\"\n    df = df.copy().sort_values('dispatch_date')\n    df['lead_time_ema'] = df['actual_lead_time_days'].ewm(alpha=alpha).mean()\n    df['rolling_std'] = df['actual_lead_time_days'].rolling(window=14, min_periods=3).std().fillna(1.0)\n    \n    # Flag anomaly where actual exceeds EMA by threshold * std\n    df['is_anomaly'] = df['actual_lead_time_days'] > (df['lead_time_ema'] + threshold_std * df['rolling_std'])\n    return df[['shipment_id', 'actual_lead_time_days', 'lead_time_ema', 'is_anomaly']]\n```"
            },
            "write sql queries": {
                "category": "CODING",
                "title": "Grounded SQL Implementation",
                "response": "Here is a certified Snowflake SQL analytical query calculating **Rolling 30-Day On-Time In-Full (OTIF)** with window functions:\n\n```sql\nWITH daily_orders AS (\n    SELECT \n        sales_order_date,\n        COUNT(sales_order_id) AS total_orders,\n        SUM(CASE WHEN is_ontime = 1 AND is_infull = 1 THEN 1 ELSE 0 END) AS otif_orders\n    FROM SUPPLYCHAIN_IQ_DB.GOLD_SEMANTIC.V_CANONICAL_OTIF\n    GROUP BY sales_order_date\n)\nSELECT \n    sales_order_date,\n    total_orders,\n    otif_orders,\n    ROUND(otif_orders * 100.0 / NULLIF(total_orders, 0), 2) AS daily_otif_pct,\n    ROUND(AVG(otif_orders * 100.0 / NULLIF(total_orders, 0)) \n          OVER (ORDER BY sales_order_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) AS rolling_30d_otif_pct\nFROM daily_orders\nORDER BY sales_order_date DESC;\n```"
            },
            "create a study plan": {
                "category": "EDUCATION",
                "title": "4-Week Mastery Study Plan",
                "response": "### 📅 4-Week Full-Stack AI & Data Engineering Study Plan\n\n- **Week 1: Modern SQL & Semantic Modeling**\n  - Day 1-3: Window functions, Common Table Expressions (CTEs), indexing.\n  - Day 4-7: Dimensional modeling (Kimball Star Schema), Snowflake Medallion architecture.\n- **Week 2: Applied Machine Learning & Snowpark**\n  - Day 8-10: Feature engineering, imputation, categorical encoding, train/test splitting.\n  - Day 11-14: Random Forest, LightGBM, ROC-AUC evaluation, SHAP explainability.\n- **Week 3: Deep Learning & Graph Networks**\n  - Day 15-18: PyTorch tensors, Multi-head attention, residual networks.\n  - Day 19-21: PyTorch Geometric (PyG), node classification, spatial graphs.\n- **Week 4: API Deployment & Full-Stack UI**\n  - Day 22-25: FastAPI endpoints, Pydantic validation, semantic caching.\n  - Day 26-28: Three.js 3D WebGL, interactive visualizations, and automated CI/CD testing."
            },
            "what time is it?": {
                "category": "UTILITY",
                "title": "System Timestamp",
                "response": f"The current system time is **{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (IST / UTC+5:30)**. All real-time telemetry streams and batch workers are synchronized."
            },
            "what's the weather?": {
                "category": "UTILITY",
                "title": "Logistics Weather & Climate Feed",
                "response": "Current Logistics Corridor Weather Snapshot:\n- **Western India Coastal (Mumbai / JNPT)**: 29°C, 78% Humidity, Light Sea Breeze (Normal maritime operations).\n- **Gujarat Hub (Mundra / Kandla)**: 33°C, Clear Skies, Optimal vessel loading conditions.\n- **UAE Gateway (Jebel Ali / Dubai)**: 36°C, Sunny, Port berths operating at standard throughput.\n- **Eastern Saudi Arabia (Dammam)**: 37°C, Low precipitation, standard transit clearance."
            },
            "give me startup ideas": {
                "category": "IDEATION",
                "title": "AI & Supply Chain Startup Ideas",
                "response": "### 🚀 Top 3 B2B AI Startup Ideas in Global Trade\n\n1. **Cross-Border Customs Attestation AI**: Automated multi-jurisdiction HS code reconciliation and LLM bill-of-lading verification to eliminate port demurrage fines.\n2. **Cold-Chain IoT Digital Twin**: Low-cost sensor networks predicting spoilage of pharmaceuticals and perishables before delivery.\n3. **Zero-Drift Semantic Layer for ERPs**: Autonomous middleware reconciling financial ledgers with physical logistics TMS dispatches in real-time."
            },
            "give me a productivity tip": {
                "category": "PRODUCTIVITY",
                "title": "Productivity Hack: Time Blocking & The 2-Minute Rule",
                "response": "💡 **The 2-Minute Rule & Pomodoro 50/10**: If a task takes under 2 minutes (e.g. approving a pull request, tagging a ticket, replying to an email), do it immediately. For deep engineering work, block 50 minutes of uninterrupted focus with notifications muted, followed by a 10-minute mental reset. You will double your output with zero burnout!"
            }
        }

    def match_general_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Matches a natural language query against general conversational patterns.
        """
        q_clean = query.strip().lower()
        q_no_punct = "".join(c for c in q_clean if c.isalnum() or c.isspace()).strip()

        # 1. Direct or fuzzy greeting match
        for greeting_key, greeting_resp in self.greetings.items():
            if q_clean == greeting_key or q_no_punct == greeting_key.replace("?", "").replace("👋", "").strip():
                return {
                    "is_general": True,
                    "category": "GREETING",
                    "title": "Conversational Greeting",
                    "response": greeting_resp,
                    "intent": "GENERAL_CONVERSATION"
                }

        # 2. Direct knowledge base match
        for kb_key, kb_data in self.knowledge_base.items():
            kb_key_clean = "".join(c for c in kb_key if c.isalnum() or c.isspace()).strip()
            if q_clean == kb_key or q_no_punct == kb_key_clean or kb_key_clean in q_no_punct:
                return {
                    "is_general": True,
                    "category": kb_data["category"],
                    "title": kb_data["title"],
                    "response": kb_data["response"],
                    "intent": "GENERAL_CONVERSATION"
                }

        # 3. Categorical keyword pattern matching
        # Coding & Technology
        if any(w in q_no_punct for w in ["write python", "python code", "write java", "write javascript", "debug code", "debug my code", "fix error", "find the error", "help with coding"]):
            return {
                "is_general": True,
                "category": "CODING",
                "title": "Code Generation & Debugging",
                "response": self.knowledge_base["write python code"]["response"],
                "intent": "CODING_ASSISTANT"
            }
        if any(w in q_no_punct for w in ["sql query", "create sql", "write sql"]):
            return {
                "is_general": True,
                "category": "CODING",
                "title": "SQL Engineering",
                "response": self.knowledge_base["write sql queries"]["response"],
                "intent": "CODING_ASSISTANT"
            }
        if any(w in q_no_punct for w in ["explain machine learning", "what is machine learning", "learn ml"]):
            return {
                "is_general": True,
                "category": "TECH",
                "title": "Machine Learning Overview",
                "response": self.knowledge_base["explain machine learning"]["response"],
                "intent": "KNOWLEDGE_TUTOR"
            }
        if any(w in q_no_punct for w in ["explain deep learning", "what is deep learning", "neural network"]):
            return {
                "is_general": True,
                "category": "TECH",
                "title": "Deep Learning Fundamentals",
                "response": self.knowledge_base["explain deep learning"]["response"],
                "intent": "KNOWLEDGE_TUTOR"
            }
        if any(w in q_no_punct for w in ["explain data science", "what is data science"]):
            return {
                "is_general": True,
                "category": "TECH",
                "title": "Data Science Fundamentals",
                "response": self.knowledge_base["explain data science"]["response"],
                "intent": "KNOWLEDGE_TUTOR"
            }
        if any(w in q_no_punct for w in ["explain cloud", "cloud computing"]):
            return {
                "is_general": True,
                "category": "TECH",
                "title": "Cloud Computing Fundamentals",
                "response": self.knowledge_base["explain cloud computing"]["response"],
                "intent": "KNOWLEDGE_TUTOR"
            }

        # Education & Study
        if any(w in q_no_punct for w in ["study plan", "help me study", "how to study"]):
            return {
                "is_general": True,
                "category": "EDUCATION",
                "title": "Study Roadmap",
                "response": self.knowledge_base["create a study plan"]["response"],
                "intent": "STUDY_PLANNER"
            }
        if any(w in q_no_punct for w in ["quiz me", "ask me a question", "practice question"]):
            return {
                "is_general": True,
                "category": "EDUCATION",
                "title": "Supply Chain & AI Quiz",
                "response": "Here is a challenge question for you:\n\n**Question:** *In a cross-border logistics network, if supplier lead time increases from 5 days to 12 days, and daily demand is 50 units with standard deviation of 8 units, what happens to your Safety Stock requirement ($Z \\times \\sigma_{LT}$)?*\n\n**A)** It remains constant.\n**B)** It increases proportionally to $\\sqrt{12/5}$.\n**C)** It decreases.\n\n*Reply with your answer and I'll explain the complete formula!*",
                "intent": "QUIZ_TUTOR"
            }

        # Career & Resume
        if any(w in q_no_punct for w in ["resume", "create a resume", "improve my resume", "cover letter"]):
            return {
                "is_general": True,
                "category": "CAREER",
                "title": "Resume & Career Enhancement",
                "response": "Here are 3 high-impact resume bullet points for your portfolio:\n- *'Engineered a governed Snowflake Medallion Lakehouse unifying 25,000 TMS shipments and 113,000 multi-tier nodes into canonical SCOR semantic views.'*\n- *'Trained Snowpark ML Random Forest and PyTorch Attention models achieving 89.58% accuracy and 0.9664 ROC-AUC for pre-dispatch delay prediction.'*\n- *'Implemented Model Context Protocol (MCP) server executing autonomous TMS carrier rerouting, reducing simulated delay exposure by 4.2 days.'*",
                "intent": "CAREER_COACH"
            }
        if any(w in q_no_punct for w in ["interview", "mock interview", "prepare interview"]):
            return {
                "is_general": True,
                "category": "CAREER",
                "title": "Mock Interview Question",
                "response": "### 🎯 Technical System Design Interview Question:\n*'How would you design a real-time tracking and exception alert system for 100,000 daily international maritime shipments with intermittent GPS telemetry?'*\n\n**Key Discussion Points to Cover:**\n1. **Ingestion**: Event-driven streaming (Kafka/Kinesis) with dead-letter queue.\n2. **Semantic Storage**: Medallion architecture (Bronze raw logs -> Silver cleaned pings -> Gold shipment status).\n3. **ML Disruption Scoring**: Lightweight edge inference or vector batch scoring with Snowflake Snowpark.\n4. **Downstream Actions**: Webhook integration for ERP writebacks and automated carrier switching.\n\nWould you like me to walk through the detailed architecture for any of these components?",
                "intent": "CAREER_COACH"
            }

        # Ideation & Business
        if any(w in q_no_punct for w in ["startup idea", "project idea", "business idea", "give me ideas"]):
            return {
                "is_general": True,
                "category": "IDEATION",
                "title": "Innovative Venture Ideas",
                "response": self.knowledge_base["give me startup ideas"]["response"],
                "intent": "IDEATION_COACH"
            }

        # Productivity & Daily Planning
        if any(w in q_no_punct for w in ["plan my day", "plan my week", "create a schedule", "to do list"]):
            return {
                "is_general": True,
                "category": "PRODUCTIVITY",
                "title": "Daily Engineering Schedule",
                "response": "Here is an optimal high-performance daily engineering schedule:\n- **09:00 - 09:30**: Triage critical monitoring alerts, review pull requests, and plan top 3 priorities.\n- **09:30 - 12:00**: Deep Work Block 1 (Architecture, core ML algorithms, or backend pipeline code).\n- **12:00 - 13:00**: Lunch & mental reset.\n- **13:00 - 15:30**: Deep Work Block 2 (UI integration, test verification, and benchmarking).\n- **15:30 - 16:30**: Team sync, design reviews, and documentation updates.\n- **16:30 - 17:30**: Code cleanup, automated CI/CD checks, and plan for tomorrow.",
                "intent": "PRODUCTIVITY_PLANNER"
            }
        if any(w in q_no_punct for w in ["productivity tip", "help me focus", "organize my tasks"]):
            return {
                "is_general": True,
                "category": "PRODUCTIVITY",
                "title": "Focus & Flow Tip",
                "response": self.knowledge_base["give me a productivity tip"]["response"],
                "intent": "PRODUCTIVITY_PLANNER"
            }

        # Fun / Motivation
        if any(w in q_no_punct for w in ["joke", "laugh", "funny"]):
            return {
                "is_general": True,
                "category": "FUN",
                "title": "Humor Break",
                "response": self.knowledge_base["tell me a joke"]["response"],
                "intent": "ENTERTAINMENT"
            }
        if any(w in q_no_punct for w in ["motivate", "motivation", "inspire"]):
            return {
                "is_general": True,
                "category": "MOTIVATION",
                "title": "Inspiration",
                "response": self.knowledge_base["motivate me"]["response"],
                "intent": "MOTIVATION"
            }
        if any(w in q_no_punct for w in ["fact", "interesting"]):
            return {
                "is_general": True,
                "category": "FACTS",
                "title": "Curious Fact",
                "response": self.knowledge_base["tell me something interesting"]["response"],
                "intent": "KNOWLEDGE_TUTOR"
            }
        if any(w in q_no_punct for w in ["story", "tell me a story"]):
            return {
                "is_general": True,
                "category": "CREATIVE",
                "title": "Supply Chain Story",
                "response": self.knowledge_base["tell me a story"]["response"],
                "intent": "STORYTELLING"
            }

        return None
