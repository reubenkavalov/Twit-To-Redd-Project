import requests
import re
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from collections import Counter
import streamlit as st


stopwords = set(nltk.corpus.stopwords.words('english'))

reddit_df = pd.read_csv('/Users/reuben/PycharmProjects/TwittToRedd/venv/reddit_df.csv')
reddit_df_stopped = pd.DataFrame()
reddit_df = reddit_df.drop(columns=["Unnamed: 0"])
reddit_df.columns = reddit_df.columns.astype("int")

reddit_df_stopped[0] = reddit_df[0]
reddit_df_stopped[1] = reddit_df[1].apply(lambda x: ' '.join([word for word in x.split() if word not in (stopwords)]))
reddit_df_stopped['full_text'] = reddit_df_stopped[1].apply(lambda x: re.sub(r'[^\w\s]', '', x))
reddit_df_stopped['full_text'] = reddit_df_stopped['full_text'].apply(lambda x: re.sub(r'[\d]', '', x))


def flatten(container):
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i


model = Doc2Vec.load('/Users/reuben/PycharmProjects/TwittToRedd/venv/d2v.model')


def get_liked_tweets(handle):
    '''
    Takes Twitter handle and extracts and parses liked tweets.

    '''
    ### Acquired from Twitter using API key and API secret key ###
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAImyAwEAAAAAyWB9oAfMqhJG66%2BeJHuUEi5wsXM%3DKOzTDPgjqoXjzERO1JmoAJfVIqjnaPdD7wUhayNjESzeytty2J'
    ###
    all_tweets = []
    url = 'https://api.twitter.com/1.1/favorites/list.json?screen_name={}'.format(handle)
    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token),
    }
    first_url_params = {
        'count': 200
    }
    first_response = requests.get(url, headers=headers, params=first_url_params)
    print(first_response)
    first_initial_split = first_response.text.split(',"text":"')
    first_t = len(first_initial_split)
    for i in range(1, first_t):
        all_tweets.append(first_initial_split[i].split(',"truncated":')[0])

    ### Regex to extract the id of the last tweet to use as pagination ###
    regsearch = re.search('(?<=(\d","id":))[\d]*', first_initial_split[first_t - 2])
    tweet_id = int(regsearch.group(0))
    ###

    ### Looping process to manually paginate through tweets ###
    page = 0
    while page < 5:
        url1 = 'https://api.twitter.com/1.1/favorites/list.json?screen_name={}&count=200&max_id={}'.format(handle,
                                                                                                           tweet_id - 1)
        response = requests.get(url1, headers=headers)
        initial_split = response.text.split(',"text":"')
        t = len(initial_split)
        for i in range(1, t):
            all_tweets.append(initial_split[i].split(',"truncated":')[0])

        ### Regex to extract the id of the last tweet to use as pagination ###
        try:
            regsearch = re.search('(?<=(\d","id":))[\d]*', initial_split[t - 2])
            tweet_id = int(regsearch.group(0))
        except:
            break
        ###

        page += 1
    return all_tweets


def RedditCategoryPredictor(twitter_handle):
    likes = get_liked_tweets(twitter_handle)
    print("Grabbed {} likes".format(len(likes)))

    joined_words = []
    for i in set(likes):
        joined_words.append("".join(i))
    posts_df = pd.DataFrame(joined_words)
    posts_df['full_text'] = posts_df[0].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    posts_df['full_text'] = posts_df['full_text'].apply(lambda x: re.sub(r'[\d]', '', x))
    posts_df['final'] = posts_df['full_text'].apply(lambda x: x.split())

    dictionary = corpora.Dictionary(posts_df['final'])
    dictionary.filter_extremes(no_below=10, no_above=0.66, keep_n=20000)
    tokens = list(flatten(posts_df['final']))
    new_vector = model.infer_vector(tokens)
    sims = model.docvecs.most_similar([new_vector], topn=50)
    final_results = []
    for i in sims:
        final_results.append(reddit_df_stopped.iloc[int(i[0])][0])
    cnt = Counter()
    for i in final_results:
        cnt[i] += 1
    st.title(max(cnt, key=cnt.get))
    cat = max(cnt, key=cnt.get)
    if cat == "Technology":
        st.markdown('* [r/technology](https://www.reddit.com/r/technology/)<br>'
                    '* [r/Android](https://www.reddit.com/r/Android/)<br>'
                    '* [r/Bitcoin](https://www.reddit.com/r/Bitcoin/)<br>'
                    '* [r/programming](https://www.reddit.com/r/programming/)<br>'
                    '* [r/apple](https://www.reddit.com/r/apple/)<br>', unsafe_allow_html=True
                    )
    if cat == "Sports":
        st.markdown('<ul>'
                    '* [r/nba](https://www.reddit.com/r/nba/)<br>'
                    '* [r/soccer](https://www.reddit.com/r/soccer/)<br>'
                    '* [r/hockey](https://www.reddit.com/r/hockey/)<br>'
                    '* [r/nfl](https://www.reddit.com/r/nfl/)<br>'
                    '* [r/formula1](https://www.reddit.com/r/formula1/)<br>'
                    '* [r/baseball](https://www.reddit.com/r/baseball/)<br>'
                    '* [r/MMA](https://www.reddit.com/r/MMA/)<br>'
                    '* [r/SquaredCircle](https://www.reddit.com/r/SquaredCircle/)<br>', unsafe_allow_html=True
                    )
    if cat == "Race, Gender, and Identity":
        st.markdown('* [r/atheism](https://www.reddit.com/r/atheism/)<br>'
                    '* [r/TwoXChromosomes](https://www.reddit.com/r/TwoXChromosomes/)<br>'
                    '* [r/MensRights](https://www.reddit.com/r/MensRights/)<br>'
                    '* [r/gaybros](https://www.reddit.com/r/gaybros/)<br>'
                    '* [r/lgbt](https://www.reddit.com/r/lgbt/)<br>', unsafe_allow_html=True
                    )
    if cat == "Places":
        st.markdown('* [r/canada](https://www.reddit.com/r/canada/)<br>'
                    '* [r/toronto](https://www.reddit.com/r/toronto/)<br>'
                    '* [r/australia](https://www.reddit.com/r/australia/)<br>'
                    '* [r/unitedkingdom](https://www.reddit.com/r/unitedkingdom/)<br>', unsafe_allow_html=True
                    )
    if cat == "News and Issues":
        st.markdown('* [r/politics](https://www.reddit.com/r/politics/)<br>'
                    '* [r/worldnews](https://www.reddit.com/r/worldnews/)<br>'
                    '* [r/news](https://www.reddit.com/r/news/)<br>'
                    '* [r/conspiracy](https://www.reddit.com/r/conspiracy/)<br>'
                    '* [r/Libertarian](https://www.reddit.com/r/Libertarian/)<br>'
                    '* [r/TrueReddit](https://www.reddit.com/r/TrueReddit/)<br>'
                    '* [r/Conservative](https://www.reddit.com/r/Conservative/)<br>'
                    '* [r/offbeat](https://www.reddit.com/r/offbeat/)<br>', unsafe_allow_html=True
                    )
    if cat == "Lifestyle and Help":
        st.markdown('* [r/trees](https://www.reddit.com/r/trees/)<br>'
                    '* [r/MakeupAddiction](https://www.reddit.com/r/MakeUpAddiction/)<br>'
                    '* [r/cats](https://www.reddit.com/r/cats/)<br>'
                    '* [r/LifeProTips](https://www.reddit.com/r/LifeProTips/)<br>'
                    '* [r/RedditLaqueristas](https://www.reddit.com/r/RedditLaqueristas/)<br>'
                    '* [r/Random_Acts_Of_Amazon](https://www.reddit.com/r/Random_Acts_Of_Amazon/)<br>'
                    '* [r/food](https://www.reddit.com/r/food/)<br>'
                    '* [r/guns](https://www.reddit.com/r/guns/)<br>'
                    '* [r/tattoos](https://www.reddit.com/r/tattoos/)<br>'
                    '* [r/corgi](https://www.reddit.com/r/corgi/)<br>'
                    '* [r/teenagers](https://www.reddit.com/r/teenagers/)<br>'
                    '* [r/GetMotivated](https://www.reddit.com/r/GetMotivated/)<br>'
                    '* [r/motorcycle](https://www.reddit.com/r/motorcycle/)<br>'
                    '* [r/sex](https://www.reddit.com/r/sex/)<br>'
                    '* [r/progresspics](https://www.reddit.com/r/progresspics/)<br>'
                    '* [r/DIY](https://www.reddit.com/r/DIY/)<br>'
                    '* [r/bicycling](https://www.reddit.com/r/bicycling/)<br>'
                    '* [r/Fitness](https://www.reddit.com/r/Fitness/)<br>'
                    '* [r/lifehacks](https://www.reddit.com/r/lifehacks/)<br>'
                    '* [r/longboarding](https://www.reddit.com/r/longboarding/)<br>'
                    '* [r/Frugal](https://www.reddit.com/r/Frugal/)<br>'
                    '* [r/drunk](https://www.reddit.com/r/drunk/)<br>'
                    '* [r/Art](https://www.reddit.com/r/Art/)<br>'
                    '* [r/loseit](https://www.reddit.com/r/loseit/)<br>'
                    '* [r/Military](https://www.reddit.com/r/Military/)<br>', unsafe_allow_html=True
                    )
    if cat == "Learning and Thinking":
        st.markdown('* [r/todayilearned](https://www.reddit.com/r/todayilearned/)<br>'
                    '* [r/science](https://www.reddit.com/r/science/)<br>'
                    '* [r/askscience](https://www.reddit.com/r/askscience/)<br>'
                    '* [r/space](https://www.reddit.com/r/space/)<br>'
                    '* [r/AskHistorians](https://www.reddit.com/r/AskHistorians/)<br>'
                    '* [r/YouShouldKnow](https://www.reddit.com/r/YouShouldKnow/)<br>'
                    '* [r/explainlikeimfive](https://www.reddit.com/r/explainlikeimfive/)<br>', unsafe_allow_html=True
                    )
    if cat == "Images, Gifs, and Videos":
        st.markdown('* [r/pics](https://www.reddit.com/r/pics/)<br>'
                    '* [r/videos](https://www.reddit.com/r/videos/)<br>'
                    '* [r/gifs](https://www.reddit.com/r/gifs/)<br>'
                    '* [r/reactiongifs](https://www.reddit.com/r/reactiongifs/)<br>'
                    '* [r/mildlyinteresting](https://www.reddit.com/r/mildlyinteresting/)<br>'
                    '* [r/woahdude](https://www.reddit.com/r/woahdude/)<br>'
                    '* [r/FiftyFifty](https://www.reddit.com/r/FiftyFifty/)<br>'
                    '* [r/FoodPorn](https://www.reddit.com/r/FoodPorn/)<br>'
                    '* [r/HistoryPorn](https://www.reddit.com/r/HistoryPorn/)<br>'
                    '* [r/wallpapers](https://www.reddit.com/r/wallpapers/)<br>'
                    '* [r/youtubehaiku](https://www.reddit.com/r/youtubehaiku/)<br>'
                    '* [r/Unexpected](https://www.reddit.com/r/Unexpected/)<br>'
                    '* [r/photoshopbattles](https://www.reddit.com/r/photoshopbattles/)<br>'
                    '* [r/AnimalsBeingJerks](https://www.reddit.com/r/AnimalsBeingJerks/)<br>'
                    '* [r/cosplay](https://www.reddit.com/r/cosplay/)<br>'
                    '* [r/EarthPorn](https://www.reddit.com/r/EarthPorn/)<br>'
                    '* [r/QuotesPorn](https://www.reddit.com/r/QuotesPorn/)<br>'
                    '* [r/awwnime](https://www.reddit.com/r/awwnime/)<br>'
                    '* [r/AbandonedPorn](https://www.reddit.com/r/AbandonedPorn/)<br>'
                    '* [r/carporn](https://www.reddit.com/r/carporn/)<br>'
                    '* [r/PerfectTiming](https://www.reddit.com/r/PerfectTiming/)<br>'
                    '* [r/OldSchoolCool](https://www.reddit.com/r/OldSchoolCool/)<br>'
                    '* [r/RoomPorn](https://www.reddit.com/r/RoomPorn/)<br>'
                    '* [r/woahdude](https://www.reddit.com/r/woahdude/)<br>'
                    '* [r/Pareidolia](https://www.reddit.com/r/Pareidolia/)<br>'
                    '* [r/MapPorn](https://www.reddit.com/r/MapPorn/)<br>'
                    '* [r/tumblr](https://www.reddit.com/r/tumblr/)<br>'
                    '* [r/techsupportgore](https://www.reddit.com/r/techsupportgore/)<br>'
                    '* [r/PrettyGirls](https://www.reddit.com/r/PrettyGirls/)<br>'
                    '* [r/itookapicture](https://www.reddit.com/r/itookapicture/)<br>', unsafe_allow_html=True
                    )
    if cat == "Humor":
        st.markdown('* [r/funny](https://www.reddit.com/r/funny/)<br>'
                    '* [r/AdviceAnimals](https://www.reddit.com/r/AdviceAnimals/)<br>'
                    '* [r/fffffffuuuuuuuuuuuu](https://www.reddit.com/r/fffffffuuuuuuuuuuuu/)<br>'
                    '* [r/4chan](https://www.reddit.com/r/4chan/)<br>'
                    '* [r/ImGoingToHellForThis](https://www.reddit.com/r/ImGoingToHellForThis/)<br>'
                    '* [r/firstworldanarchists](https://www.reddit.com/r/firstworldanarchists/)<br>'
                    '* [r/circlejerk](https://www.reddit.com/r/circlejerk/)<br>'
                    '* [r/MURICA](https://www.reddit.com/r/MURICA/)<br>'
                    '* [r/facepalm](https://www.reddit.com/r/facepalm/)<br>'
                    '* [r/Jokes](https://www.reddit.com/r/Jokes/)<br>'
                    '* [r/wheredidthesodago](https://www.reddit.com/r/wheredidthesodago/)<br>'
                    '* [r/polandball](https://www.reddit.com/r/polandball/)<br>'
                    '* [r/TrollXChromosomes](https://www.reddit.com/r/TrollXChromosomes/)<br>'
                    '* [r/comics](https://www.reddit.com/r/comics/)<br>'
                    '* [r/nottheonion](https://www.reddit.com/r/nottheonion/)<br>'
                    '* [r/britishproblems](https://www.reddit.com/r/britishproblems/)<br>'
                    '* [r/TumblrInAction](https://www.reddit.com/r/TumblrInAction/)<br>'
                    '* [r/onetruegod](https://www.reddit.com/r/onetruegod/)<br>', unsafe_allow_html=True
                    )
    if cat == "Entertainment - Other (Movies/Music/Franchies/Misc)":
        st.markdown('* [r/Music](https://www.reddit.com/r/Music/)<br>'
                    '* [r/movies](https://www.reddit.com/r/movies/)<br>'
                    '* [r/harrypotter](https://www.reddit.com/r/harrypotter/)<br>'
                    '* [r/StarWars](https://www.reddit.com/r/StarWars/)<br>'
                    '* [r/DaftPunk](https://www.reddit.com/r/DaftPunk/)<br>'
                    '* [r/hiphopheads](https://www.reddit.com/r/hiphopheads/)<br>'
                    '* [r/anime](https://www.reddit.com/r/anime/)<br>'
                    '* [r/comicbooks](https://www.reddit.com/r/comicbooks/)<br>'
                    '* [r/geek](https://www.reddit.com/r/geek/)<br>'
                    '* [r/batman](https://www.reddit.com/r/batman/)<br>'
                    '* [r/TheLastAirbender](https://www.reddit.com/r/TheLastAirbender/)<br>'
                    '* [r/Naruto](https://www.reddit.com/r/Naruto/)<br>'
                    '* [r/FanTheories](https://www.reddit.com/r/FanTheories/)<br>', unsafe_allow_html=True
                    )
    if cat == "Entertainment - Television":
        st.markdown('* [r/arresteddevelopment](https://www.reddit.com/r/arresteddevelopment/)<br>'
                    '* [r/gameofthrones](https://www.reddit.com/r/gameofthrones/)<br>'
                    '* [r/doctorwho](https://www.reddit.com/r/doctorwho/)<br>'
                    '* [r/mylittlepony](https://www.reddit.com/r/mylittlepony/)<br>'
                    '* [r/community](https://www.reddit.com/r/community/)<br>'
                    '* [r/breakingbad](https://www.reddit.com/r/breakingbad/)<br>'
                    '* [r/adventuretime](https://www.reddit.com/r/adventuretime/)<br>'
                    '* [r/startrek](https://www.reddit.com/r/startrek/)<br>'
                    '* [r/TheSimpsons](https://www.reddit.com/r/TheSimpsons/)<br>'
                    '* [r/futurama](https://www.reddit.com/r/futurama/)<br>'
                    '* [r/HIMYM](https://www.reddit.com/r/HIMYM/)<br>'
                    '* [r/DunderMifflin](https://www.reddit.com/r/DunderMifflin/)<br>'
                    '* [r/thewalkingdead](https://www.reddit.com/r/thewalkingdead/)<br>', unsafe_allow_html=True
                    )
    if cat == "Entertainment - Gaming":
        st.markdown('* [r/gaming](https://www.reddit.com/r/gaming/)<br>'
                    '* [r/leagueoflegends](https://www.reddit.com/r/leagueoflegends/)<br>'
                    '* [r/pokemon](https://www.reddit.com/r/pokemon/)<br>'
                    '* [r/Minecraft](https://www.reddit.com/r/Minecraft/)<br>'
                    '* [r/starcraft](https://www.reddit.com/r/starcraft/)<br>'
                    '* [r/Games](https://www.reddit.com/r/Games/)<br>'
                    '* [r/DotA2](https://www.reddit.com/r/DotA2/)<br>'
                    '* [r/skyrim](https://www.reddit.com/r/skyrim/)<br>'
                    '* [r/tf2](https://www.reddit.com/r/tf2/)<br>'
                    '* [r/magicTCG](https://www.reddit.com/r/magicTCG/)<br>'
                    '* [r/wow](https://www.reddit.com/r/wow/)<br>'
                    '* [r/KerbalSpaceProgram](https://www.reddit.com/r/KerbalSpaceProgram/)<br>'
                    '* [r/mindcrack](https://www.reddit.com/r/mindcrack/)<br>'
                    '* [r/Fallout](https://www.reddit.com/r/Fallout/)<br>'
                    '* [r/roosterteeth](https://www.reddit.com/r/roosterteeth/)<br>'
                    '* [r/Planetside](https://www.reddit.com/r/Planetside/)<br>'
                    '* [r/gamegrumps](https://www.reddit.com/r/gamegrumps/)<br>'
                    '* [r/battlefield3](https://www.reddit.com/r/battlefield3/)<br>'
                    '* [r/zelda](https://www.reddit.com/r/zelda/)<br>'
                    '* [r/darksouls](https://www.reddit.com/r/darksouls/)<br>'
                    '* [r/masseffect](https://www.reddit.com/r/masseffect/)<br>', unsafe_allow_html=True
                    )
    if cat == "Emotional Reaction Fuel":
        st.markdown('* [r/WTF](https://www.reddit.com/r/arresteddevelopment/)<br>'
                    '* [r/aww](https://www.reddit.com/r/gameofthrones/)<br>'
                    '* [r/cringepics](https://www.reddit.com/r/doctorwho/)<br>'
                    '* [r/JusticePorn](https://www.reddit.com/r/mylittlepony/)<br>'
                    '* [r/MorbidReality](https://www.reddit.com/r/community/)<br>'
                    '* [r/rage](https://www.reddit.com/r/breakingbad/)<br>'
                    '* [r/mildlyinfuriating](https://www.reddit.com/r/adventuretime/)<br>'
                    '* [r/creepy](https://www.reddit.com/r/startrek/)<br>'
                    '* [r/creepyPMs](https://www.reddit.com/r/TheSimpsons/)<br>'
                    '* [r/nosleep](https://www.reddit.com/r/futurama/)<br>'
                    '* [r/nostalgia](https://www.reddit.com/r/HIMYM/)<br>', unsafe_allow_html=True
                    )
    if cat == "Discussion and Stories":
        st.markdown('* [r/AskReddit](https://www.reddit.com/r/arresteddevelopment/)<br>'
                    '* [r/IAmA](https://www.reddit.com/r/gameofthrones/)<br>'
                    '* [r/bestof](https://www.reddit.com/r/doctorwho/)<br>'
                    '* [r/fatpeoplestories](https://www.reddit.com/r/mylittlepony/)<br>'
                    '* [r/pettyrevenge](https://www.reddit.com/r/community/)<br>'
                    '* [r/TalesFromRetail](https://www.reddit.com/r/breakingbad/)<br>'
                    '* [r/DoesAnybodyElse](https://www.reddit.com/r/adventuretime/)<br>'
                    '* [r/CrazyIdeas](https://www.reddit.com/r/startrek/)<br>', unsafe_allow_html=True
                    )
    return max(cnt)
