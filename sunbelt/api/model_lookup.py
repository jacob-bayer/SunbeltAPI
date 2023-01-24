from .models import *

HOURS_TO_WAIT = {'subreddit': 24,}

lookup_dict = {'subreddit': {'main': Subreddit,
                             'version': SubredditVersion,
                             'detail': SubredditDetail},
               'comment': {'main': Comment,
                           'version': CommentVersion,
                           'detail': CommentDetail,
                        #    'gilding': CommentGilding,
                        #    'awarding': CommentAwarding
                        },
               'post': {'main': Post,
                        'version': PostVersion,
                        'detail': PostDetail,
                        # 'gilding': PostGilding,
                        # 'awarding': PostAwarding,
                        # 'media': PostMedia,
                        # 'secure_media': PostSecureMedia,
                        # 'media_embed': PostMediaEmbed
                        },
                'account': {'main': Account,
                            'version': AccountVersion,
                            'detail': AccountDetail}}