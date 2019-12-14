# Twit-To-Redd-Project
Recommends subreddits from Reddit based on specified Twitter user "likes"


# Goal of the Project
To bridge the gap between Twitter users and Reddit users, as many people who enjoy one form of social media/entertainment enjoy the other. The app will take your Twitter handle, and recommend subreddits (forums dedicated to specific topics on Reddit) based on liked tweets. Then, the user will be able to look up these suggested subreddits in a searchbox that finds them a short list of other similar subreddits. The entire interactive process is done in seconds!

# The Data

In order to train a model to classify tweets into a certain "category" of subreddits, it needs to be trained on those different categories. The following categories were selected based on [this Reddit post](https://www.reddit.com/r/TheoryOfReddit/comments/1f7hqc/the_200_most_active_subreddits_categorized_by/):
* Discussion and Stories 
* Emotional Reaction Fuel
* Entertainment - Gaming
* Entertainment - Television
* Entertainment - Other (Movies/Music/Franchies/Misc) 
* Humor
* Images, Gifs, and Videos
* Learning and Thinking
* Lifestyle and Help
* News and Issues
* Places
* Race, Gender, and Identity
* Sports
* Technology
Each category had 5-25 subreddits in it; The titles of the top 1000 posts from each subreddit are scraped in order to get a large corpus for each category. This results in the acquisition of ~170,000 posts.

![DataFrame of Posts](images/postsdf.png)




