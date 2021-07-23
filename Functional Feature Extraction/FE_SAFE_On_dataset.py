# -*- coding: utf-8 -*-

"""
License: The usage of the code is limited to research. Commercial use of the code is not allowed.
"""

import re
import sys
from collections import Counter

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tag.stanford import StanfordPOSTagger

#from DescriptionPerDescriptionEvaluation import Documents, Evaluation

#path_to_model = "../stanford-postagger-full-2016-10-31/models/english-bidirectional-distsim.tagger"
#path_to_jar = "../stanford-postagger-full-2016-10-31/stanford-postagger.jar"

path_to_model = "C:/Kafil/Lab/Python/FE_SAFE.py/stanford-postagger-2016-10-31/models/english-bidirectional-distsim.tagger"
path_to_jar = "C:/Kafil/Lab/Python/FE_SAFE.py/stanford-postagger-2016-10-31/stanford-postagger.jar"

st_tagger = StanfordPOSTagger(path_to_model, path_to_jar)

"""
 This class is able to extract app features from descriptions. This algorithm is optimized for the following apps
"""


class SAFE:
    def __init__(self):
        self.debug = False
        self.test = False  # use a test string instead of the whole description
        self.feature_word_threshold = 4
        self.test_string = """View microsoft office documents, PDFs, photos, videos, and more""".lower()
        self.feature_list = []
        self.raw_feature_list = []
        self.subordinate_conjunctions = ["after", "although", "because", "before", "even if", "even though", "if",
                                         "in order that	once", "provided that", "rather than", "since", "so that",
                                         "than", "that", "though", "unless", "until", "when", "whenever", "where",
                                         "whereas", "wherever", "whether", "while", "why"]  # "as"
        self.relative_pronouns = ["that", "which", "whichever", "who", "whoever", "whom", "whose", "whosever",
                                  "whomever"]
        self.review_filter_keywords = ["crash", "crashed", "crashes", "app", "apps", "version", "gmail", "love", "hate",
                                       "please", "fix", "easy", "use", "have", "is", "using", "do", "help", "great",
                                       "think", "need", "version", "versions", "does", "piss", "good", "trash", "thank",
                                       "bug", "try", "well","ios", "yahoo"]

        self.review_filter_keywords + stopwords.words('english')
        self.stoplist = set(stopwords.words('english'))
        self.stoplist = {"to"}
        self.symbol_pattern = r"[a-zA-Z]"
        self.bracket_pattern = r"\([^)]*\)"
        self.email_pattern = "r'[\w\.-]+@[\w\.-]+'"
        grammar = r"""
                    NP: {<V.*><NN.*><NN.*>+}
                    VN: {<V.*><NN.*>+}
                    VPN:{<V.*><PR.*>?<JJ*>?<NN.*>+}
                    VAN:{<V.*><JJ*><NN.*>+}
                    VIN:{<V.*><IN><NN.*>?<NN.*>}
                    NJN:{<NN><JJ*><NN.*>+}
                    NN:{<NN><NN.*>+}
                  """
        review_grammar = r"""
                    VN: {<V.*><NN.*>+}
                    VPN:{<V.*><PR.*>?<JJ*>?<NN.*>+}
                    VIN:{<V.*><IN><NN.*>?<NN.*>}
                    NN:{<NN><NN.*>+}
                  """
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.parser = nltk.RegexpParser(grammar)
        self.review_parser = nltk.RegexpParser(review_grammar)
        self.words_not_to_lemmatize = ["sms", "ics", "use", "uses"]
        self.sentence_filter = ["www", "http", "https", ".com", ".de"]
        self.sentence_filter_quotes = ["\"", "“", "”"]
        self.app_name = "evernote".lower()
        self.description = ""

    def extract_sentences(self, input_string):
        split_sentences = input_string.split("\n")
        tmp_sentences = []

        sentences = []
        for sentence in split_sentences:
            for s in nltk.sent_tokenize(sentence):
                tmp_sentences.append(s)

        for sentence in tmp_sentences:
            for s in sentence.split(":") and sentence.split(" - "):
                sentences.append(s.strip())

        return sentences

    def get_wordnet_pos(self, tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def lemmatize_sentences(self, tokens_per_sentence):
        lemmatized_tokens = []
        for tokens in tokens_per_sentence:
            tokens_per_sentence_tmp = []
            for (token, tag) in tokens:
                tokens_per_sentence_tmp.append(self.lemmatizer.lemmatize(token, self.get_wordnet_pos(tag)))
            lemmatized_tokens.append(tokens_per_sentence_tmp)
        return lemmatized_tokens

    def remove_text_in_brackets(self, sentences):
        p = re.compile(self.bracket_pattern)
        processed_sentences = []
        for sentence in sentences:
            processed_sentences.append(re.sub(p, '', sentence))
        return processed_sentences

    def remove_symbols(self, input_list):
        """test the first two and the last char of a sentence. If it does not contain a letter remove that part"""
        output_list = []
        for s in input_list:
            s = s.strip()
            s = re.sub(":", "", s)
            if s and len(s) >= 2:
                last_char_pos = s.__len__() - 1
                # check the first two chars and transform the string if necessary
                if not re.match(self.symbol_pattern, s[0]):
                    if not re.match(self.symbol_pattern, s[1]):
                        s = s[2:]
                        last_char_pos -= 2
                    else:
                        s = s[1:]
                        last_char_pos -= 1

                # check the last char and transform the string if necessary
                if len(s) <= last_char_pos:
                    if not re.match(self.symbol_pattern, s[last_char_pos]):
                        s = s[:last_char_pos]

                output_list.append(s)

        if self.debug:
            print("symbol remover------->")
            for output in output_list:
                print(output)
            print("<------symbol remover\n")
        return output_list

    def remove_symbols_from_review(self, input_list):
        output_list = []
        for s in input_list:
            s = s.strip()
            s = re.sub(r"\W+", " ", s)
            s = re.sub("\"", "", s)

            output_list.append(s)

        return output_list

    def remove_subordinate_clauses(self, sentences):
        processed_sentences = []
        for sentence in sentences:
            # check if there is a subordinate conjunction in the beginning or in the middle of the sentence
            if not any(word in sentence.split(" ") for word in self.subordinate_conjunctions):
                processed_sentences.append(sentence)
                # for word in sentence.split(" "):
                #     if word in self.subordinate_conjunctions:
                #         print(word)
                #         print(sentence)

        return processed_sentences

    def filter_sentences(self, sentences):
        processed_sentences = []
        # remove sentences that e.g. contain URLs because they are used to address the contact to the publisher
        for sentence in sentences:
            if not any(word in sentence for word in self.sentence_filter):
                processed_sentences.append(sentence)

        # remove sentences that contain quotations since they are reviews/statements of external people
        tmp_processed_sentences = processed_sentences
        processed_sentences = []
        for sentence in tmp_processed_sentences:
            quote_counter = 0
            for quote in self.sentence_filter_quotes:
                quote_counter += sentence.count(quote)
            if quote_counter < 2:
                processed_sentences.append(sentence)

        # remove sentences that contain email addresses as they are used for providing a contact to the publisher
        tmp_processed_sentences = processed_sentences
        processed_sentences = []
        for sentence in tmp_processed_sentences:
            if re.search(self.email_pattern, sentence) is None:
                processed_sentences.append(sentence)

        return processed_sentences

    def tokenize_sentence(self, sentences):
        index = 0
        tokens_per_sentence = []
        if type(sentences) is list:
            for sentence in sentences:
                tokens_per_sentence.append(nltk.word_tokenize(sentence))
                index += 1
            return tokens_per_sentence
        elif type(sentences) is str:
            tokens_per_sentence.append(nltk.word_tokenize(sentences))
            return tokens_per_sentence

    def tokenize_reviews(self, sentences):
        index = 0
        tokens_per_sentence = []
        if type(sentences) is list:
            for sentence in sentences:
                tokens_per_sentence.append(sentence.split())
                index += 1
            return tokens_per_sentence
        elif type(sentences) is str:
            tokens_per_sentence.append(sentences.split())
            return tokens_per_sentence

    def expand_all_contractions(self, sentences):
        """Expands all contractions within the documents
        :returns documents with expanded contractions"""
        expanded_sentences = []
        for sentence in sentences:
            expanded_tokens = ""
            for token in sentence.split():
                expanded_tokens += (" " + (self.expand_contraction(token)))
            expanded_sentences.append(expanded_tokens)

        return expanded_sentences

    def expand_contraction(self, word):
        """expands word if word is a contraction
        :param word to check
        :returns expanded word"""
        contractions = {
            "ain't": "am not",  # are not; is not; has not; have not",
            "aren't": "are not",  # ; am not",
            "can't": "cannot",
            "can't've": "cannot have",
            "'cause": "because",
            "could've": "could have",
            "couldn't": "could not",
            "couldn't've": "could not have",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hadn't've": "had not have",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he had",  # , / he would",
            "he'd've": "he would have",
            "he'll": "he shall",  # / he will",
            "he'll've": "he shall have",  # / he will have",
            "he's": "he has",  # / he is",
            "how'd": "how did",
            "how'd'y": "how do you",
            "how'll": "how will",
            "how's": "how has",  # / how is / how does",
            "i'd": "i had",  # / I would",
            "i'd've": "i would have",
            "i'll": "i will",  # / I shal",
            "i'll've": "i will have",  # / I shall have",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",  # / it had",
            "it'd've": "it would have",
            "it'll": "it will",  # / it shall",
            "it'll've": "it will have",  # / it shall have",
            "it's": "it is",  # / it has",
            "let's": "let us",
            "ma'am": "madam",
            "mayn't": "may not",
            "might've": "might have",
            "mightn't": "might not",
            "mightn't've": "might not have",
            "must've": "must have",
            "mustn't": "must not",
            "mustn't've": "must not have",
            "needn't": "need not",
            "needn't've": "need not have",
            "o'clock": "of the clock",
            "oughtn't": "ought not",
            "oughtn't've": "ought not have",
            "shan't": "shall not",
            "sha'n't": "shall not",
            "shan't've": "shall not have",
            "she'd": "she had",  # / she would",
            "she'd've": "she would have",
            "she'll": "she shall",  # / she will",
            "she'll've": "she shall have",  # / she will have",
            "she's": "she is",  # / she has",
            "should've": "should have",
            "shouldn't": "should not",
            "shouldn't've": "should not have",
            "so've": "so have",
            "so's": "so is",  # / so as",
            "that'd": "that would",  # / that had",
            "that'd've": "that would have",
            "that's": "that is",  # / that has",
            "there'd": "there had",  # / / there would",
            "there'd've": "there would have",
            "there's": "there is",  # / there has",
            "they'd": "they had",  # / they would",
            "they'd've": "they would have",
            "they'll": "they shall / they will",
            "they'll've": "they will have",  # / they shall have",
            "they're": "they are",
            "they've": "they have",
            "to've": "to have",
            "wasn't": "was not",
            "we'd": "we had ",  # / we would",
            "we'd've": "we would have",
            "we'll": "we will",
            "we'll've": "we will have",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what will",  # / what will",
            "what'll've": "what will have",  # / what shall have",
            "what're": "what are",
            "what's": "what is",  # / what has",
            "what've": "what have",
            "when's": "when is ",  # / when has",
            "when've": "when have",
            "where'd": "where did",
            "where's": "where is",  # / where has",
            "where've": "where have",
            "who'll": "who will",  # / who will",
            "who'll've": "who will have ",  # / who will have",
            "who's": "who is",  # / who has",
            "who've": "who have",
            "why's": "why is",  # / why has",
            "why've": "why have",
            "will've": "will have",
            "won't": "will not",
            "won't've": "will not have",
            "would've": "would have",
            "wouldn't": "would not",
            "wouldn't've": "would not have",
            "y'all": "you all",
            "y'all'd": "you all would",
            "y'all'd've": "you all would have",
            "y'all're": "you all are",
            "y'all've": "you all have",
            "you'd": "you had",  # / you would",
            "you'd've": "you would have",
            "you'll": "you will",  # / you shall",
            "you'll've": "you will have",  # / you shall have",
            "you're": "you are",
            "you've": "you have"
        }

        if word in contractions.keys():
            word = contractions[word]
        return word

    def remove_stopwords(self, tokens_per_sentence, extract_from_review=False):
        stopped_tokens_per_sentence = []
        self.stoplist.add(self.app_name)
        if extract_from_review:
            for item in self.review_filter_keywords:
                self.stoplist.add(item)
            self.stoplist |= set(stopwords.words('english'))

        for tokens in tokens_per_sentence:
            tokens_per_sentence_tmp = []
            for token in tokens:
                if token not in self.stoplist:
                    tokens_per_sentence_tmp.append(token)
                else:
                    tokens_per_sentence_tmp.append(" ")
            # print("tokens_per_sentence_tmp: ", tokens_per_sentence_tmp)
            stopped_tokens_per_sentence.append(tokens_per_sentence_tmp)

        return stopped_tokens_per_sentence

    def pos_tag_tokenized_sentences(self, tokens_per_sentence):
        pos_tags_per_sentence = []
        for tokens in tokens_per_sentence:
            # just create pos tags if the token array is not empty
            if tokens:
                pos_tags_per_sentence.append(st_tagger.tag(tokens))
                # print(nltk.pos_tag(tokens))

        if self.debug:
            for d in pos_tags_per_sentence:
                for s in d:
                    print(s[0] + "_" + s[1], end=" ")
                print("\n")

        return pos_tags_per_sentence

    def extract_features_from_complex_lists(self, tokens_per_sentence):
        """extracts features from complex lists in sentences like:
                send and receive videos, messages and emojis
                Features:
                    - send videos
                    - send message
                    - send emojis
                    - receive videos
                    - receive message
                    - receive emojis

            The extracted features are added to self.feature_list.
            Sentences that contain those features are removed from tokens_per_sentence.
            The remaining sentences are returned for further processing.
        """

        # 1. check for indicators of such sentences by counting the conjunction "and" and "or"
        """ possible cases
            case 1: "Write, collect and capture ideas as searchable notes, notebooks, checklists and to-do lists"
            case 2: "Discuss and annotate notes and drafts"
            case 3: "Use camera capture to easily scan and comment on pieces of paper, including printed documents,
                     business cards, handwriting and sketches"
            case 4: "to let you message and call friends and family, so you don't have to pay for every message or call"
            case 5: "send and receive attachments"
            case 6: "View documents, PDFs, photos, videos, and more"
        """
        remaining_sentences = []
        for tokens in tokens_per_sentence:
            conj_counter = Counter([j if i == 'and' and j == "CC" else None for i, j in tokens])
            cc_on_right_side = None
            is_case_1 = False
            is_case_2 = False
            is_case_3 = False
            is_case_4 = False
            is_case_5 = False
            is_case_6 = False
            if conj_counter["CC"] >= 1:
                # check which case we have
                try:
                    left_side_tokens = tokens[:tokens.index(('and', 'CC'))]
                    right_side_tokens = tokens[tokens.index(('and', 'CC')):]
                    if conj_counter["CC"] == 1 and len(right_side_tokens) < len(left_side_tokens):
                        cc_on_right_side = True

                except ValueError:
                    left_side_tokens = None
                    right_side_tokens = None

                # check for case 1-4
                if left_side_tokens:
                    # check if there is a comma on the left side, which would indicate case 1
                    # if there are no commas, we have to check if we have case 2 or 3
                    left_side_comma_counter = Counter([j if "," == j else None for i, j in left_side_tokens])
                    right_side_comma_counter = Counter([j if "," == j else None for i, j in right_side_tokens])
                    if conj_counter["CC"] >= 2:
                        if left_side_comma_counter[","] > 0:
                            is_case_1 = True
                        elif left_side_comma_counter[","] == 0 and len(
                                left_side_tokens) < 3:  # just allow a max. of 2 words
                            is_case_2 = True
                        elif left_side_comma_counter[","] == 0 and right_side_comma_counter[","] > 0:
                            if right_side_comma_counter[","] > 1:
                                is_case_3 = True
                            else:
                                is_case_4 = True
                    elif cc_on_right_side and left_side_comma_counter[","] >= 1:
                        is_case_6 = True
                # check for case 5
                # check if there is a verb on the left and on the right side of a conjunction
                try:
                    left_side_is_verb = tokens[tokens.index(('and', 'CC')) - 1:tokens.index(('and', 'CC'))][0][
                                            1] == "VB"
                    right_side_is_verb = tokens[tokens.index(('and', 'CC')) + 1:tokens.index(('and', 'CC')) + 2][0][
                                             1] == "VB"
                    if left_side_is_verb and right_side_is_verb:
                        is_case_5 = True
                except IndexError:
                    # ignore
                    is_case_5 = False

            if is_case_1:
                # print("CASE 1")
                self.extract_from_case_1(tokens)
            elif is_case_2:
                # print("CASE 2")
                self.extract_from_case_2(tokens)
            elif is_case_3:
                # print("CASE 3")
                self.extract_from_case_3(tokens)
            elif is_case_4:
                # print("CASE 4")
                self.extract_from_case_4(tokens)
            elif is_case_5:
                # print("CASE 5")
                self.extract_from_case_5(tokens)
            elif is_case_6:
                # print("CASE 6")
                self.extract_from_case_6(tokens)
            else:
                remaining_sentences.append(tokens)

        return remaining_sentences

    def extract_from_case_1(self, tokens):
        # remove POS tags and transform tokens to string
        left_side = ""
        for t in tokens[:tokens.index(('and', 'CC')) + 2]:
            left_side += " %s" % str(t[0]).lower()

        right_side = ""
        for t in tokens[tokens.index(('and', 'CC')) + 2:]:
            right_side += " %s" % str(t[0])

        starting_feature_words = left_side.split(" and ")[0].split(",")
        starting_feature_words.append(left_side.split(" and ")[1])
        starting_feature_words = [x.strip() for x in starting_feature_words]

        combining_features = right_side.split(" and ")[0].split(",")
        combining_features.append(right_side.split(" and ")[1])
        combining_features = [x.strip() for x in combining_features]

        for s in starting_feature_words:
            for c in combining_features:
                if s and c:
                    # self.add_feature("%s %s" % (s, c))
                    self.add_raw_feature("%s %s" % (s, c))
                    # print("%s %s" % (s, c))

    def extract_from_case_2(self, tokens):
        # the code of self.extract_from_case_1 also works for this case, but we still have to differentiate both
        # cases because the sentence structure is different
        self.extract_from_case_1(tokens)

    def extract_from_case_3(self, tokens):
        # remove POS tags and transform tokens to string
        left_side = ""
        for t in tokens[:tokens.index(('and', 'CC')) + 2]:
            left_side += " %s" % str(t[0]).lower()

        right_side = ""
        for t in tokens[tokens.index(('and', 'CC')) + 2:]:
            right_side += " %s" % str(t[0])

        no_of_words = len(left_side.split(" and ")[0].split(" "))
        if no_of_words > 2:  # just allow two word combination, if there are more words = substring to the last two
            # create a substring of the last two words in front of the word "and"
            left_side = " ".join((left_side.rsplit(" ", 4))[1:])
        starting_feature_words = left_side.split(" and ")[0].split(",")
        starting_feature_words.append(left_side.split(" and ")[1])
        starting_feature_words = [x.strip() for x in starting_feature_words]

        combining_features = right_side.split(" and ")[0].split(",")
        combining_features.append(right_side.split(" and ")[1])
        combining_features = [x.strip() for x in combining_features]

        for s in starting_feature_words:
            for c in combining_features:
                if s and c:
                    # self.add_feature("%s %s" % (s, c))
                    self.add_raw_feature("%s %s" % (s, c))
                    # print("%s %s" % (s, c))

    def extract_from_case_4(self, tokens):
        """in this case we do not care about the right side of the comma, as we assume that
            having a single comma & more than 3 words after it and before any other conjunction,
            we do not have to combine the left side with the right one as they don't belong together
        """
        # remove POS tags and transform tokens to string
        allowed_pos_tags = ("V", "J", "N", "C")
        left_side = ""
        for t in tokens[:tokens.index(('and', 'CC')) + 2]:
            if str(t[1]).startswith(allowed_pos_tags):
                left_side += " %s" % str(t[0]).lower()
            else:
                left_side = ""

        right_side = ""
        for t in tokens[tokens.index(('and', 'CC')) + 2:tokens.index((',', ','))]:
            right_side += " %s" % str(t[0])

        starting_feature_words = left_side.split(" and ")[0].split(",")
        starting_feature_words.append(left_side.split(" and ")[1])
        starting_feature_words = [x.strip() for x in starting_feature_words]

        combining_features = right_side.split(" and ")[0].split(",")
        # print("\n", tokens, "\n")
        if len(right_side.split(" and ")) > 1:
            combining_features.append(right_side.split(" and ")[1])
        combining_features = [x.strip() for x in combining_features]

        for s in starting_feature_words:
            for c in combining_features:
                if s and c:
                    # self.add_feature("%s %s" % (s, c))
                    self.add_raw_feature("%s %s" % (s, c))
                    # print("%s %s" % (s, c))

    def extract_from_case_5(self, tokens):
        # remove POS tags and transform tokens to string
        left_side = []
        for t in tokens[:tokens.index(('and', 'CC')) + 2]:
            if not t[0] == "and":
                left_side.append(str(t[0]).lower().strip())

        right_side = ""
        for t in tokens[tokens.index(('and', 'CC')) + 2:]:
            right_side += " %s" % str(t[0])

        for l in left_side:
            self.add_raw_feature("%s %s" % (l.strip(), right_side.strip()))

    def extract_from_case_6(self, tokens):
        # remove POS tags and transform tokens to string
        left_side = tokens[0][0]

        right_side_str = ""
        for t in tokens[1:]:
            right_side_str += " %s" % str(t[0])

        right_side = []
        for cc in right_side_str.split("and"):
            for part in cc.split(","):
                part = part.strip()
                if part:
                    right_side.append(part)

        for r in right_side:
            self.add_raw_feature("%s %s" % (left_side.strip(), r.strip()))

    def chunk_sentences(self, pos_tagged_sentences):
        pos_tagged_sentences += self.raw_feature_list
        chunks = []
        if self.debug:
            print("chunk sentences --------------------->")
            for sentence in pos_tagged_sentences:
                print("pos_tagged_sentences", sentence)
            print("<--------------------- chunk sentences\n")
        for sentence in pos_tagged_sentences:
            try:
                result = self.parser.parse(sentence)
                for subtree in result.subtrees():
                    if subtree.label() == 'NP' or \
                                    subtree.label() == 'VN' or \
                                    subtree.label() == 'VPN' or \
                                    subtree.label() == 'VAN' or \
                                    subtree.label() == 'VIN' or \
                                    subtree.label() == 'NN' or \
                                    subtree.label() == 'NJN':
                        feature = ""
                        for element in subtree:
                            if len(element) > 2:
                                for e in element:
                                    feature += " %s" % (str(e[0]).strip())
                            else:
                                feature += " %s" % (str(element[0]).strip())
                        chunks.append(feature)
                        if len(feature.strip().split(" ")) >= 2:  # do not add features that are just a single word
                            self.add_feature(feature.strip().lower())
            except:
                print("err: ", sentence)
                sys.stderr.write()
                pass

        return chunks

    def chunk_review_sentences(self, pos_tagged_sentences):
        pos_tagged_sentences += self.raw_feature_list
        chunks = []
        if self.debug:
            print("chunk sentences --------------------->")
            for sentence in pos_tagged_sentences:
                print("pos_tagged_sentences", sentence)
            print("<--------------------- chunk sentences\n")
        for sentence in pos_tagged_sentences:
            try:
                result = self.parser.parse(sentence)
                for subtree in result.subtrees():
                    if subtree.label() == 'NP' or \
                                    subtree.label() == 'VN' or \
                                    subtree.label() == 'VPN' or \
                                    subtree.label() == 'VIN' or \
                                    subtree.label() == 'NN':
                        feature = ""
                        for element in subtree:
                            if len(element) > 2:
                                for e in element:
                                    feature += " %s" % (str(e[0]).strip())
                            else:
                                feature += " %s" % (str(element[0]).strip())
                        chunks.append(feature)
                        if len(feature.strip().split(" ")) >= 2:  # do not add features that are just a single word
                            self.add_feature(feature.strip().lower())
            except:
                print("err: ", sentence)
                sys.stderr.write()
                pass

        return chunks

    def post_filter_app_features(self):
        """ This function

            1. removes the features from the self.feature_list that have too many words.
            As language ambiguity is very high, we cannot cover all possibilities in the choice of words and
            sentence structures. Therefore, the final list might contain wrong entries, which are typically
            long sentences. This methods removes those self.feature_list entries that have more words than specified in
            self.feature_word_threshold.

            2. filters features that contain non-informative information. This method is keyword based and uses
            keywords that the authors found by looking into extracted features.
            For example the sentence: "view documents and more" resolves in the app features: "view documents" and
            "view more", whereas, the second feature is labeled as non-informative, since 'more' is not defined

            3. filter app features that contain grammar subtrees because of their complexity

            4. remove duplicates
        """
        # 1.
        self.feature_list = [feature for feature in self.feature_list if
                             not len(feature.split(" ")) > self.feature_word_threshold]

        # 3.
        self.feature_list = [feature for feature in self.feature_list if
                             "(" not in feature]

        # 4.
        self.feature_list = set(self.feature_list)

    def post_filter_app_features_from_reviews(self):
        """ This function

            1. removes the features from the self.feature_list that have too many words.
            As language ambiguity is very high, we cannot cover all possibilities in the choice of words and
            sentence structures. Therefore, the final list might contain wrong entries, which are typically
            long sentences. This methods removes those self.feature_list entries that have more words than specified in
            self.feature_word_threshold.

            2. filters features that contain non-informative information. This method is keyword based and uses
            keywords that the authors found by looking into extracted features.
            For example the sentence: "view documents and more" resolves in the app features: "view documents" and
            "view more", whereas, the second feature is labeled as non-informative, since 'more' is not defined

            3. filter app features that contain grammar subtrees because of their complexity

            4. do not allow word duplicates in one app feature like: "email email"

            5. remove duplicates
        """
        # 1.
        self.feature_list = [feature for feature in self.feature_list if
                             not len(feature.split(" ")) > self.feature_word_threshold]

        # 2.
        # self.review_filter_keywords = stopwords.words('english')
        # self.feature_list = [feature for feature in self.feature_list if
        #                      not any(word in feature for word in self.review_filter_keywords)]

        # 3.
        self.feature_list = [feature for feature in self.feature_list if "(" not in feature]

        # 4.
        self.feature_list = [feature for feature in self.feature_list if feature.split()[0] != feature.split()[1]]

        # 5.
        self.feature_list = set(self.feature_list)

    def print_final_features(self):
        print("\n Features:")
        for feature in set(self.feature_list):
            print(feature)

    def write_features_to_file(self):
        feature_file = open("feature_file_appdescriptions.txt", "a")
        feature_file.write("\n\n-------\n%s\n------\n" % self.app_name)
        for feature in self.feature_list:
            feature_file.write("%s\n" % feature)

    def debug_sentences(self, sentences):
        # print("sentences------->")
        for sentence in sentences:
            print(sentence)
        print("<------sentences\n\n")

    def add_raw_feature(self, feature):
        pos_tagged_features = self.pos_tag_tokenized_sentences(self.tokenize_sentence(feature))
        for element in pos_tagged_features:
            self.raw_feature_list.append(element)

    def add_feature(self, feature):
        self.feature_list.append(feature.strip())

    # def evaluate(self):
    #     document = Documents()
    #     truth_set = document.load_app_features_by_app_name(self.app_name)
    #     test_set = self.feature_list

    #     evalutation = Evaluation()
    #     evalutation.evaluate(truth_set, test_set)

    def print_final_features_pos_tags(self):
        print("------------------")
        for feature in self.feature_list:
            pos_tagged_features = self.pos_tag_tokenized_sentences(self.tokenize_sentence(feature))
            for element in pos_tagged_features:
                print(element)
        print("------------------")

    def extract_from_review(self, review):
        self.feature_list = []
        self.raw_feature_list = []
        self.review = review.lower()

        """The method that acts like a facade and controls all method calls"""
        sentences = self.extract_sentences(self.review)
        sentences = self.remove_text_in_brackets(sentences)
        sentences = self.filter_sentences(sentences)
        # sentences = self.remove_subordinate_clauses(sentences)
        sentences = self.expand_all_contractions(sentences)
        sentences = self.remove_symbols_from_review(sentences)

        tokens_per_sentence = self.tokenize_sentence(sentences)
        tokens_per_sentence = self.pos_tag_tokenized_sentences(tokens_per_sentence)
        tokens_per_sentence = self.lemmatize_sentences(tokens_per_sentence)
        tokens_per_sentence = self.remove_stopwords(tokens_per_sentence, True)

        pos_tags_per_sentence = self.pos_tag_tokenized_sentences(tokens_per_sentence)
        pos_tags_per_sentence = self.extract_features_from_complex_lists(pos_tags_per_sentence)
        if self.debug:
            print("features before chunking ------------->")
            self.print_final_features()
            print("<------------- features before chunking\n")

        sentence_chunks = self.chunk_review_sentences(pos_tags_per_sentence)

        self.post_filter_app_features_from_reviews()
        # self.print_final_features()
        # self.print_final_features_pos_tags()
        # self.write_features_to_file()
        # self.evaluate()

        return self.feature_list

    def extract_from_description(self, description):
        self.feature_list = []
        self.raw_feature_list = []
        self.description = description

        """The method that acts like a facade and controls all method calls"""
        sentences = self.extract_sentences(self.description)
        sentences = self.remove_text_in_brackets(sentences)
        sentences = self.filter_sentences(sentences)
        sentences = self.remove_symbols(sentences)
        sentences = self.remove_subordinate_clauses(sentences)

        if self.debug:
            self.debug_sentences(sentences)
        tokens_per_sentence = self.tokenize_sentence(sentences)
        tokens_per_sentence = self.remove_stopwords(tokens_per_sentence)

        pos_tags_per_sentence = self.pos_tag_tokenized_sentences(tokens_per_sentence)
        pos_tags_per_sentence = self.extract_features_from_complex_lists(pos_tags_per_sentence)
        if self.debug:
            print("features before chunking ------------->")
            self.print_final_features()
            print("<------------- features before chunking\n")

        sentence_chunks = self.chunk_sentences(pos_tags_per_sentence)

        self.post_filter_app_features()
        self.print_final_features()
        # self.print_final_features_pos_tags()
        # self.write_features_to_file()
        # self.evaluate()

        return self.feature_list


if __name__ == '__main__':
    ############
    # Extract from a single descriptions
    ############
    # example_description = """

    #     Kik has a brand new look! It's more fun and easy to use, so you can spend less time hunting for photos and GIFs and more time chatting with friends.

    #     Quickly find friends, start groups and discover bots with the "+" menu
    #     It's easier to send your favorite photos, GIFs, stickers and smileys - they're under the text field for easy access
    #     When you have a lot to say and send several messages in a row, chat bubbles will group together
    #     Looking for faded D? We made the S, D and R colors darker!
            
    # """
    
    example_description = """Kik has a brand new look! It's more fun and easy to use, so you can spend less time hunting for photos and GIFs and more time chatting with friends.
Quickly find friends, start groups and discover bots with the "+" menu
It's easier to send your favorite photos, GIFs, stickers and smileys - they're under the text field for easy access
When you have a lot to say and send several messages in a row, chat bubbles will group together
Looking for faded D? We made the S, D and R colors darker!  """

    print(example_description)
    # example_review = """
    # 5 Cannot write more than two captions While sending images.....??
    # 3 sometimes very slow, screen offs quickly, Pl help improve this many thanks.
    # 3 unable to delete one call instead all list of call you made..
    # 5 Please make an ipad version of whatsapp.
    # 5 This is a good app but I think people should have snapchat because snapchat has cute filters and you could call and video call and put stuff in your story and you can add friends on snapchat and you can also text your friends in snapchat and play games.
    # 5 great. I use it loads and find it really helpful. I pretty much made this review to ask this question. my friends' group chats always have different colours for people's names but mine has no colours. Why is this?
    # 5 Still an awesome app. Sometimes i wish WhatsApp have on and off button, coz i just want to ignore everybody for a moment. ??
    # 5 all r very nice but we needed some more clarity in pic while video calling
    # 1 plzz add this feature then show the profile picture only one person like in a status
    # 5 best way to connect to my friends locally and internationally and share clear videos and pictures!!
    # 1 When we will forwarding the message limitations of 5 people, but we need Unlimited people/group. After the complain it's not changed.
    # 5 I use it a lot, really great app.. But I need to know.. Would the blocked contacts be informed or notified if I change my phone number?
    # 4 Great messenger. But still no full darkmode.
    # 3 sometimes message notification not ringing
    # 1 cant share video
    # 3 it's very interesting yo share your sadness in status.
    # 5 Whatsapp, can you make *message editing* option?
    # 3 please add default status downloader update it quick for further more subscribers
    # 3 it OK but the call cut off in the middle of the conversation ...need. to be more clear
    # 5 So convenient specially with video call
    # 1 We need to be able to use whatsapp without data or WiFi
    # 4 incoming call doesnt show up on lockscreen
    # 3 video calls not clear ??
    # 5 just a little suggestion, can whatsapp make an option where you can schedule a mute for certain group. instead of setting the group mute for 8 hours everyday, it already been scheduled to mute from this hour to this hour on this certain day. i think this is very helpful to mute a group during working days.
    # 5 A nice improvement... Better than the last.
    # 4 i can't see if what time the person who is online or not..
    # 3 This is garbage, I prefer the old version
    # 4 It's nice. But seeing people's comments on other people's statuses would be more fun.
    # 1 update version is not working properly. mia1 ph. do something as early as possible.
    # 4 Great app, but dislikes updates
    # 5 I love whatsapp!! So useful...to write with...call or send videos and photos and links and share and copy paste!!
    # 5 Its good cause its reception is always good ,sound quality during calls wheather its video or voice or overseas calll is always on perfection, Keep up the good work
    # 4 picture-in-picture player doesn't work anymore and sends me to YouTube anyway
    # """
    example_review = """
    So convenient specially with video call"""

    feature_extractor = SAFE()
    # x= feature_extractor.extract_from_description(example_description)
    # y= feature_extractor.extract_from_review(example_description)
    # print("------",x)
    # print("++++++",y)

    whatsnew_f= open('C:\\Users\\mdkafiluddin\\Desktop\\Research\\Experiments\\RQ2\\kik\\kik_whatsnew.txt', encoding="utf-8", errors="ignore")
    whatsnew_text = whatsnew_f.read()
    whatsnew_f.close()
    # print(str(whatsnew_text))
    set_A=feature_extractor.extract_from_description(whatsnew_text)
    set_B=feature_extractor.extract_from_review(whatsnew_text)
    set_C=set_A.union(set_B)
    
    print("Union++++",set_C)
    # print("R++++",feature_extractor.extract_from_review((whatsnew_text)))