# popflix
"Because scrolling for 45 minutes is a real horror movie."
*PopFlix* is a smart movie recommendation system powered by machine learning. Just pick a movie you love, and PopFlix will suggest five similar films — complete with posters and titles.

📌 Project Highlights -
🔍 Content-Based Filtering: Uses movie overviews and metadata (genres, keywords, etc.) to compute similarities.
📐 Cosine Similarity: Quantifies how close two movies are in terms of their content.
🎥 TMDB Dataset: Real-world data including titles, overviews, cast, crew, genres, and more.
⚡ Fast & Accurate recommendations in real-time.

🧠 How It Works :
Preprocessing: Cleans and merges relevant movie data.
Feature Engineering: Creates a combined string of keywords, genres, cast, director, etc.
Vectorization: Uses CountVectorizer or TfidfVectorizer to convert text to vectors.
Similarity Scoring: Computes cosine similarity between movie vectors.
Recommendation: Recommends top N similar movies based on your input.

📁 Dataset Used : [https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata?resource=download](https://drive.google.com/file/d/1cCkwiVv4mgfl20ntgY3n4yApcWqqZQe6/view)

🛠 Built With -
Python 
Pandas, NumPy,
Scikit-learn,
TMDB Dataset,
Jupyter Notebook



