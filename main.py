import numpy as np
import pandas as pd
from textblob import TextBlob
from read_wiki import read_top_25_articles
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

TOP_25_FILE : str = 'top_25.csv'

if __name__ == "__main__":
    # Comment this if you don't want updated data
    # articles : dict[str, list[str]] = read_top_25_articles()
    # articles_df : pd.DataFrame = pd.DataFrame(data=articles, columns=['name', 'text'])
    # articles_df.to_csv(TOP_25_FILE, index=False)

    # Comment this if you wanna just work on previous data
    articles_df : pd.DataFrame = pd.read_csv(TOP_25_FILE)

    # Make matrix of articles and words used for all articles
    count_vectorizer = CountVectorizer(stop_words='english')
    article_terms_matrix = count_vectorizer.fit_transform(articles_df['text'])
    article_terms_matrix = article_terms_matrix.toarray()
    # Make matrix of term frequency and inverse document frequency
    tf_idf_vectorizer = TfidfVectorizer(stop_words='english')
    tf_idf_matrix = tf_idf_vectorizer.fit_transform(articles_df['text'])
    tf_idf_matrix = tf_idf_matrix.toarray()

    # Word frequencies
    # each article
    for i in range(25):
        word_freq = article_terms_matrix[i]
        word_freq_df = pd.DataFrame({'word': count_vectorizer.get_feature_names_out(), 'frequency': word_freq})
        word_freq_df.sort_values(by=['frequency', 'word'], ascending=False, inplace=True)
        print(f'Word Frequencies of Article: {articles_df.loc[i, 'name']}')
        print(word_freq_df.head(10))
    # all articles combined
    word_freq = np.sum(article_terms_matrix, axis=0)
    word_freq_df = pd.DataFrame({'word': count_vectorizer.get_feature_names_out(), 'frequency': word_freq})
    word_freq_df.sort_values(by=['frequency', 'word'], ascending=False, inplace=True)
    print('Word Frequencies of All Articles:')
    print(word_freq_df.head(10))

    # Article similarity
    print('Article Similarities:')
    article_similarities = cosine_similarity(tf_idf_matrix)
    for i in range(25):
        most_similar = np.argsort(article_similarities[i])[-2] # the last one is 1, which is similarity with self
        print(f'Article most similar to {articles_df.loc[i, 'name']} is {articles_df.loc[most_similar, 'name']} with score of: {article_similarities[i][most_similar]}')
        average_similarity = np.mean(np.sort(article_similarities[i])[:len(article_similarities)])
        print(f'The average similarity score is: {average_similarity}')

    # Grouping words by topic
    nmf_model = NMF(n_components=2, random_state=100)
    topic_matrix = nmf_model.fit_transform(tf_idf_matrix)
    # Get top words for each topic
    feature_names = tf_idf_vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(nmf_model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-100 - 1:-1]]
        print(f"Topic {topic_idx}: {', '.join(top_words)}")

    # Sentiment Analysis
    articles_df['sentiment'] = articles_df['text'].apply(lambda x: TextBlob(x).sentiment.polarity)

