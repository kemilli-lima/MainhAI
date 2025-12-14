import re
import contractions
from nltk                             import pos_tag, SnowballStemmer
from nltk.tokenize                    import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('stopwords')

language = "portuguese"
lemmatizer = nltk.stem.WordNetLemmatizer()
param_stemmer = SnowballStemmer(language)
stopwords_pt = stopwords.words(language)


def remove_palavras_pequenas_grandes(tokens):
  return [token for token in tokens if len(token) > 2 and len(token) < 16]

def remove_stopwords(tokens, stopwords_pt):
  return [token for token in tokens if token not in stopwords_pt]

def stemming(tokens, stemmer):
  return [stemmer.stem(token) for token in tokens]

def corrigir_documento(document):
  return contractions.fix(document)

def get_wordnet_pos(treebank_tag):
  if treebank_tag.startswith('J'):
    return wordnet.ADJ
  elif treebank_tag.startswith('V'):
    return wordnet.VERB
  elif treebank_tag.startswith('N'):
    return wordnet.NOUN
  elif treebank_tag.startswith('R'):
    return wordnet.ADV
  else:
    return None


def lemmatize(tokens):
  lemmatized_tokens = []
  pos_tagged = pos_tag(tokens)
  for token, tag in pos_tagged:
    wordnet_pos = get_wordnet_pos(tag) or wordnet.NOUN
    lemmatized_tokens.append(lemmatizer.lemmatize(token, pos=wordnet_pos))

  return lemmatized_tokens


def process_corpus(corpus, stopwords: list[str]):
    for i in stopwords: stopwords_pt.append(i)
    corpus_processed = []
    for document in corpus:
        document = document.lower()
        document = re.sub(r'\b\d+[a-zA-Zºª]*\b', '', document)
        document = re.sub(r'\b\d+(?:[\.,-]?\d+)*\b', '', document)
        document = re.sub(r'[^a-zA-ZáéíóúãõâêîôûàèìòùçÁÉÍÓÚÃÕÂÊÎÔÛÀÈÌÒÙÇ\s]', '', document)
        tokens = word_tokenize(document.strip().lower())
        tokens = remove_palavras_pequenas_grandes(tokens)
        tokens = remove_stopwords(tokens, stopwords_pt)
        tokens = stemming(tokens, param_stemmer)
        tokens = lemmatize(tokens)
        tokens = remove_stopwords(tokens, stopwords_pt)
        corpus_processed.append(" ".join(tokens))
    return corpus_processed


corpus = ""
corpus_processed = process_corpus(corpus)