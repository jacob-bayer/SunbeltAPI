from .models import *

model_aliases = {'comments':'comment',
                'author' : 'account',
                'posts' : 'post'}

lookup_dict = {'subreddit': {'Main': Subreddit, 'Detail': SubredditDetail},
               'comment': {'Main': Comment,'Detail': CommentDetail},
               'post': {'Main': Post,'Detail': PostDetail},
                'account': {'Main': Account, 'Detail': AccountDetail}
                }