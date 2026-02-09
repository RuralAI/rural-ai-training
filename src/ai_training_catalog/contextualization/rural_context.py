"""Rural context definitions: mappings, examples, datasets, and use cases.

This module defines how generic AI training content gets adapted for
rural communities — agriculture, rural healthcare, small-town business,
natural resource management, and community development.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RuralUseCase:
    """A single rural-contextualized use case for an AI concept."""
    concept: str
    urban_example: str
    rural_example: str
    dataset_suggestion: str
    exercise_prompt: str


@dataclass
class RuralDomainContext:
    """Rural context for a specific AI skill domain."""
    domain: str
    overview: str
    why_it_matters: str
    use_cases: list[RuralUseCase] = field(default_factory=list)
    local_datasets: list[str] = field(default_factory=list)
    community_projects: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Example replacement mappings (urban → rural)
# ---------------------------------------------------------------------------

EXAMPLE_REPLACEMENTS: dict[str, str] = {
    # Regression examples
    "predict house prices": "predict farmland values based on soil quality, water access, and crop history",
    "stock price prediction": "crop yield prediction based on weather, soil, and planting data",
    "predict sales": "predict seasonal farm produce demand at local markets",
    "housing prices": "farmland and rural property values",
    "real estate": "agricultural land assessment",
    "stock market": "commodity prices (corn, wheat, livestock)",
    "customer churn": "farmer cooperative membership retention",
    "retail sales": "farm stand and farmers market sales",

    # Classification examples
    "spam detection": "classifying crop diseases from leaf photos",
    "email classification": "sorting agricultural extension service requests by urgency",
    "sentiment analysis of tweets": "analyzing farmer forum posts to identify common challenges",
    "fraud detection": "detecting livestock health anomalies from sensor data",
    "image classification of cats and dogs": "classifying crop types or weed species from drone images",
    "handwriting recognition": "identifying plant species from leaf shapes",
    "face recognition": "livestock identification and tracking",

    # Clustering examples
    "customer segmentation": "grouping farms by soil type, climate zone, and crop patterns",
    "market segmentation": "identifying rural community needs clusters",
    "user behavior clustering": "grouping weather patterns that affect regional harvests",
    "recommendation system": "recommending crop varieties based on local soil and climate data",
    "product recommendation": "suggesting farming equipment or techniques for similar farms",

    # NLP examples
    "chatbot": "agricultural advisory chatbot for rural farmers",
    "text summarization": "summarizing weather reports and agricultural bulletins",
    "machine translation": "translating agricultural guides into local languages",
    "question answering": "answering farming questions from extension service knowledge bases",

    # Computer Vision examples
    "self-driving cars": "autonomous tractors and precision agriculture equipment",
    "object detection in traffic": "detecting pests, diseases, or weeds in crop fields",
    "facial recognition": "livestock monitoring and health assessment",
    "medical imaging": "rural telemedicine — analyzing medical images where specialists are scarce",
    "surveillance": "monitoring water levels in irrigation systems",

    # General
    "e-commerce": "rural online marketplace connecting farmers to buyers",
    "social media": "community bulletin boards and farmer networks",
    "ride-sharing": "rural transportation and logistics coordination",
    "smart city": "smart farming and rural IoT",
    "healthcare AI": "rural telehealth and remote patient monitoring",
    "fintech": "agricultural microfinance and crop insurance",
}

# ---------------------------------------------------------------------------
# Domain-specific rural contexts
# ---------------------------------------------------------------------------

ML_BASICS_RURAL = RuralDomainContext(
    domain="ml_basics",
    overview=(
        "Machine Learning fundamentals applied to rural challenges — from predicting "
        "crop yields and optimizing irrigation to classifying livestock health and "
        "forecasting market prices for agricultural commodities."
    ),
    why_it_matters=(
        "Rural communities face unique challenges: limited access to experts, vast "
        "land areas to monitor, weather-dependent livelihoods, and resource constraints. "
        "ML can amplify the impact of limited resources by automating analysis, "
        "enabling early warning systems, and providing data-driven decision support "
        "to farmers, rural health workers, and community planners."
    ),
    use_cases=[
        RuralUseCase(
            concept="Linear Regression",
            urban_example="Predicting house prices from square footage and location",
            rural_example="Predicting crop yield from rainfall, soil pH, fertilizer amount, and planting date",
            dataset_suggestion="USDA Crop Yield data or local agricultural extension records",
            exercise_prompt=(
                "Build a regression model that predicts corn yield per acre using weather data "
                "(rainfall, temperature, sunlight hours) and soil properties. Compare your model's "
                "predictions with actual yields from your county's agricultural data."
            ),
        ),
        RuralUseCase(
            concept="Logistic Classification",
            urban_example="Classifying emails as spam or not spam",
            rural_example="Classifying whether a cow is healthy or sick based on sensor readings",
            dataset_suggestion="Livestock health monitoring datasets or FAO animal health records",
            exercise_prompt=(
                "Train a classifier that takes daily measurements (temperature, activity level, "
                "feed intake, milk production) and predicts whether a dairy cow needs veterinary "
                "attention. What accuracy can you achieve? What's the cost of a false negative?"
            ),
        ),
        RuralUseCase(
            concept="Decision Trees",
            urban_example="Deciding whether to approve a bank loan",
            rural_example="Deciding which crop to plant based on soil, season, market prices, and water availability",
            dataset_suggestion="Regional crop profitability databases, weather station data",
            exercise_prompt=(
                "Create a decision tree that recommends which crop a farmer should plant in a "
                "given season based on soil type, expected rainfall, current market prices, and "
                "available irrigation. Visualize the tree and explain the decisions."
            ),
        ),
        RuralUseCase(
            concept="K-Means Clustering",
            urban_example="Segmenting customers by purchasing behavior",
            rural_example="Grouping farmland parcels by soil quality, water access, and productivity",
            dataset_suggestion="Soil survey data from USDA NRCS or local land management offices",
            exercise_prompt=(
                "Use clustering to group farms in your region into 3-5 categories based on soil "
                "properties, elevation, and proximity to water. What management recommendations "
                "would you make for each cluster?"
            ),
        ),
        RuralUseCase(
            concept="Random Forest",
            urban_example="Predicting customer churn for a subscription service",
            rural_example="Predicting which fields are at risk of pest infestation",
            dataset_suggestion="Historical pest outbreak data combined with weather and crop rotation records",
            exercise_prompt=(
                "Build a random forest model to predict pest risk for fields in your area. "
                "Use features like crop type, previous year's pest history, nearby vegetation, "
                "temperature, and humidity. Which features are most important?"
            ),
        ),
        RuralUseCase(
            concept="Cross-Validation & Model Evaluation",
            urban_example="Evaluating a model on held-out test data from an A/B test",
            rural_example="Validating a yield prediction model across different growing seasons and regions",
            dataset_suggestion="Multi-year crop data from multiple counties or districts",
            exercise_prompt=(
                "Take your crop yield model and evaluate it using k-fold cross-validation. "
                "Does it perform equally well across different years? Different regions? "
                "What does this tell you about the model's reliability for farmers?"
            ),
        ),
        RuralUseCase(
            concept="Feature Engineering",
            urban_example="Creating features from user clickstream data",
            rural_example="Creating features from raw weather station data for agricultural models",
            dataset_suggestion="NOAA weather station data + USDA crop calendars",
            exercise_prompt=(
                "Starting with raw daily weather data (temperature, precipitation, wind), "
                "engineer useful features for a crop model: growing degree days, cumulative "
                "rainfall, frost risk indicators, drought indices. Which features improve "
                "prediction the most?"
            ),
        ),
    ],
    local_datasets=[
        "USDA National Agricultural Statistics Service (NASS) — free crop and livestock data",
        "NOAA Climate Data Online — weather station records by county",
        "USDA NRCS Web Soil Survey — soil properties for any US location",
        "FAO STAT — global agriculture, food, and land use data",
        "NASA POWER — solar and meteorological data for agriculture",
        "Kaggle Agriculture datasets — crowd-sourced farm data",
        "OpenAg / MIT Open Agriculture Initiative data",
        "CHIRPS — rainfall estimates for data-sparse regions",
        "Sentinel-2 satellite imagery — free crop monitoring from space",
    ],
    community_projects=[
        "Build a crop recommendation app for local farmers based on their soil test results",
        "Create a weather alert system that texts farmers when frost or drought conditions are predicted",
        "Develop a simple pest identification tool using phone camera photos",
        "Map soil quality across your county using public survey data and visualization tools",
        "Analyze 10 years of local market prices to help farmers decide when to sell",
        "Build a water usage optimizer for a community irrigation district",
    ],
)

DEEP_LEARNING_RURAL = RuralDomainContext(
    domain="deep_learning",
    overview=(
        "Deep learning applied to rural challenges — computer vision for crop and "
        "livestock monitoring, time-series forecasting for weather and markets, and "
        "NLP for agricultural knowledge systems."
    ),
    why_it_matters=(
        "Deep learning excels at processing images, sensor data, and text at scale — "
        "exactly the kinds of data abundant in rural settings (satellite imagery, IoT "
        "sensors, weather records, agricultural bulletins). Even small rural organizations "
        "can leverage pre-trained models and transfer learning."
    ),
    use_cases=[
        RuralUseCase(
            concept="Convolutional Neural Networks (CNNs)",
            urban_example="Classifying images of products for an online store",
            rural_example="Detecting plant diseases from smartphone photos of crop leaves",
            dataset_suggestion="PlantVillage dataset (54,000+ images of healthy and diseased crops)",
            exercise_prompt=(
                "Fine-tune a pre-trained CNN (like ResNet) on the PlantVillage dataset to "
                "classify tomato leaf diseases. Deploy it as a simple web app that a farmer "
                "can use by uploading a phone photo."
            ),
        ),
        RuralUseCase(
            concept="Recurrent Neural Networks (RNNs/LSTMs)",
            urban_example="Predicting next-day stock prices from historical trends",
            rural_example="Forecasting river water levels for flood early warning in rural communities",
            dataset_suggestion="USGS Water Resources streamflow data",
            exercise_prompt=(
                "Train an LSTM on 5 years of daily river gauge data to predict water levels "
                "3 days ahead. At what lead time does accuracy drop below useful? How could "
                "this help a rural community prepare for flooding?"
            ),
        ),
        RuralUseCase(
            concept="Transfer Learning",
            urban_example="Adapting an ImageNet model to classify fashion items",
            rural_example="Adapting an ImageNet model to identify livestock breeds or wildlife on trail cameras",
            dataset_suggestion="iNaturalist dataset or custom photos from local farms",
            exercise_prompt=(
                "Use transfer learning to adapt a pre-trained model to identify 5 common "
                "livestock breeds using only 50 photos per breed. Compare results with and "
                "without data augmentation."
            ),
        ),
    ],
    local_datasets=[
        "PlantVillage — crop disease image dataset",
        "Sentinel-2 / Landsat satellite imagery — free from ESA and USGS",
        "USGS streamflow and water quality data",
        "iNaturalist — species identification images",
        "Global Fishing Watch — marine resource monitoring",
    ],
    community_projects=[
        "Build a crop disease detection app using transfer learning and phone cameras",
        "Create a flood early warning system using river gauge data and LSTMs",
        "Develop a satellite image classifier that monitors deforestation in your watershed",
        "Train a model to count livestock in drone footage for ranchers",
    ],
)

AI_STRATEGY_RURAL = RuralDomainContext(
    domain="ai_strategy",
    overview=(
        "AI strategy for rural organizations — cooperatives, agricultural extension "
        "services, rural health clinics, and community development agencies."
    ),
    why_it_matters=(
        "Rural organizations often have smaller budgets but large geographic coverage. "
        "A focused AI strategy can help them do more with less: automate routine tasks, "
        "reach remote constituents, and make better decisions with limited data."
    ),
    use_cases=[
        RuralUseCase(
            concept="AI Roadmap",
            urban_example="Building an AI roadmap for a Fortune 500 company",
            rural_example="Building an AI roadmap for a regional farmer cooperative",
            dataset_suggestion="Cooperative operational data, member surveys, market records",
            exercise_prompt=(
                "Draft a 12-month AI adoption roadmap for a 500-member farmer cooperative. "
                "Identify 3 high-impact, low-cost AI use cases they could start with, "
                "considering their limited IT staff and budget."
            ),
        ),
    ],
    local_datasets=[],
    community_projects=[
        "Interview 5 local rural organizations about their data challenges and draft AI opportunity assessments",
        "Create a cost-benefit analysis template for rural AI projects",
    ],
)

AI_ETHICS_RURAL = RuralDomainContext(
    domain="ai_ethics",
    overview=(
        "AI ethics through a rural lens — addressing bias in agricultural data, "
        "ensuring fair access to AI tools across the digital divide, protecting "
        "farmer data privacy, and building trust in AI-driven recommendations."
    ),
    why_it_matters=(
        "Rural communities are often underrepresented in training data, leading to "
        "biased models. Connectivity gaps create unequal access to AI tools. Farmer "
        "data privacy is a growing concern as precision agriculture expands. Ethical "
        "AI practices ensure these communities benefit from — not are harmed by — AI."
    ),
    use_cases=[
        RuralUseCase(
            concept="Bias and Fairness",
            urban_example="Detecting racial bias in facial recognition systems",
            rural_example="Detecting geographic bias in crop recommendation models trained mostly on data from large commercial farms",
            dataset_suggestion="Compare model performance on small vs. large farm data",
            exercise_prompt=(
                "Take a crop yield model and test whether it performs equally well for "
                "small farms (<50 acres) vs. large operations (>1000 acres). If not, "
                "what causes the disparity and how would you fix it?"
            ),
        ),
    ],
    local_datasets=[],
    community_projects=[
        "Audit an agricultural AI tool for bias against small-scale or minority farmers",
        "Draft a data privacy policy for a farmer cooperative that collects field-level data",
        "Create a community guide: 'Your Rights When AI Systems Affect Your Farm or Community'",
    ],
)


# All rural contexts indexed by domain
RURAL_CONTEXTS: dict[str, RuralDomainContext] = {
    "ml_basics": ML_BASICS_RURAL,
    "deep_learning": DEEP_LEARNING_RURAL,
    "ai_strategy": AI_STRATEGY_RURAL,
    "ai_ethics": AI_ETHICS_RURAL,
}
