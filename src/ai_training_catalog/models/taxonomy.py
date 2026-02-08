"""Skill taxonomy: maps each SkillDomain to subtopics and search keywords.

The taxonomy drives both the discovery agent (query generation) and the
content categoriser (keyword matching).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .resource import SkillDomain


class TaxonomyNode(BaseModel):
    domain: SkillDomain
    display_name: str
    subtopics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


TAXONOMY: list[TaxonomyNode] = [
    # ---- Technical domains ----
    TaxonomyNode(
        domain=SkillDomain.ML_BASICS,
        display_name="Machine Learning Fundamentals",
        subtopics=[
            "supervised learning", "unsupervised learning", "feature engineering",
            "model evaluation", "cross-validation", "bias-variance tradeoff",
        ],
        keywords=[
            "machine learning", "regression", "classification", "clustering",
            "decision tree", "random forest", "SVM", "scikit-learn", "gradient descent",
            "overfitting", "training set", "test set", "feature selection",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.DEEP_LEARNING,
        display_name="Deep Learning",
        subtopics=[
            "neural networks", "backpropagation", "convolutional networks",
            "recurrent networks", "attention mechanisms", "transfer learning",
        ],
        keywords=[
            "deep learning", "neural network", "CNN", "RNN", "LSTM", "transformer",
            "PyTorch", "TensorFlow", "Keras", "backpropagation", "activation function",
            "dropout", "batch normalization", "GPU training",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.NLP,
        display_name="Natural Language Processing",
        subtopics=[
            "text classification", "named entity recognition", "sentiment analysis",
            "machine translation", "question answering", "text generation",
        ],
        keywords=[
            "NLP", "natural language processing", "tokenization", "embedding",
            "word2vec", "BERT", "GPT", "language model", "text mining",
            "corpus", "spaCy", "Hugging Face", "seq2seq",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.COMPUTER_VISION,
        display_name="Computer Vision",
        subtopics=[
            "image classification", "object detection", "image segmentation",
            "generative models for images", "video analysis",
        ],
        keywords=[
            "computer vision", "image recognition", "object detection", "YOLO",
            "ResNet", "image segmentation", "OpenCV", "convolutional",
            "data augmentation", "bounding box",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.MLOPS,
        display_name="MLOps & Production ML",
        subtopics=[
            "model deployment", "CI/CD for ML", "experiment tracking",
            "model monitoring", "feature stores", "ML pipelines",
        ],
        keywords=[
            "MLOps", "model deployment", "MLflow", "Kubeflow", "model serving",
            "feature store", "experiment tracking", "model registry",
            "containerization", "Docker", "Kubernetes", "CI/CD",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.GENERATIVE_AI,
        display_name="Generative AI",
        subtopics=[
            "large language models", "prompt engineering", "fine-tuning",
            "RAG", "diffusion models", "AI agents",
        ],
        keywords=[
            "generative AI", "LLM", "large language model", "prompt engineering",
            "fine-tuning", "RLHF", "diffusion model", "Stable Diffusion",
            "ChatGPT", "RAG", "retrieval augmented", "AI agent", "langchain",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.REINFORCEMENT_LEARNING,
        display_name="Reinforcement Learning",
        subtopics=[
            "Markov decision processes", "Q-learning", "policy gradient",
            "multi-agent RL", "reward shaping",
        ],
        keywords=[
            "reinforcement learning", "RL", "Q-learning", "policy gradient",
            "reward", "environment", "agent", "Markov decision", "exploration",
            "exploitation", "OpenAI Gym",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.DATA_ENGINEERING,
        display_name="Data Engineering for AI",
        subtopics=[
            "data pipelines", "data warehousing", "ETL",
            "data quality", "streaming data",
        ],
        keywords=[
            "data engineering", "ETL", "data pipeline", "Apache Spark",
            "data warehouse", "data lake", "Airflow", "Kafka",
            "data quality", "data governance",
        ],
    ),
    # ---- Business domains ----
    TaxonomyNode(
        domain=SkillDomain.AI_STRATEGY,
        display_name="AI Strategy",
        subtopics=[
            "AI roadmap", "AI maturity model", "build vs buy",
            "AI use case identification", "organizational readiness",
        ],
        keywords=[
            "AI strategy", "digital transformation", "AI adoption",
            "AI roadmap", "AI maturity", "use case", "competitive advantage",
            "AI initiative", "executive", "business strategy",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.AI_ETHICS,
        display_name="AI Ethics & Responsible AI",
        subtopics=[
            "fairness", "bias detection", "explainability",
            "privacy", "accountability", "AI safety",
        ],
        keywords=[
            "AI ethics", "responsible AI", "fairness", "bias", "explainability",
            "interpretability", "XAI", "privacy", "GDPR", "accountability",
            "AI safety", "alignment", "transparency",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.AI_PROJECT_MANAGEMENT,
        display_name="AI Project Management",
        subtopics=[
            "ML project lifecycle", "team structure", "agile for AI",
            "stakeholder management", "risk management",
        ],
        keywords=[
            "AI project management", "ML lifecycle", "data science team",
            "agile", "scrum", "stakeholder", "risk management",
            "project planning", "cross-functional", "delivery",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.AI_ROI,
        display_name="AI Return on Investment",
        subtopics=[
            "cost-benefit analysis", "AI value measurement",
            "total cost of ownership", "scaling AI",
        ],
        keywords=[
            "AI ROI", "return on investment", "cost-benefit", "business value",
            "total cost", "scaling AI", "monetization", "KPI",
            "business case", "value measurement",
        ],
    ),
    TaxonomyNode(
        domain=SkillDomain.AI_GOVERNANCE,
        display_name="AI Governance & Compliance",
        subtopics=[
            "model risk management", "regulatory compliance",
            "AI audit", "documentation standards",
        ],
        keywords=[
            "AI governance", "model risk", "compliance", "regulation",
            "audit", "documentation", "EU AI Act", "model card",
            "risk assessment", "policy",
        ],
    ),
]
