# -*- coding: utf-8 -*-
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Identity, Integer, Text, text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'posts'}

    post_id = Column(BigInteger, primary_key=True, index=True)
    modified_at = Column(DateTime, nullable=False)
    #created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    reddit_post_id = Column(Text)
    reddit_account_id = Column(Text)
    reddit_subreddit_id = Column(Text)
    subreddit_name_prefixed = Column(Text)
    title = Column(Text)
    gilded = Column(BigInteger)
    selftext = Column(Text)
    approved_at_utc = Column(Text)
    downs = Column(BigInteger)
    subreddit_type = Column(Text)
    ups = Column(BigInteger)
    upvote_ratio = Column(Float(53))
    permalink = Column(Text)

   
    def to_dict(self):
        return {
        "post_id" : self.post_id,
        "modified_at" : str(self.modified_at.strftime('%d-%m-%Y %H:%M:%S')),
        #"created_at" : str(self.created_at.strftime('%d-%m-%Y %H:%M:%S')),
        "reddit_post_id" : self.reddit_post_id,
        "reddit_account_id" : self.reddit_account_id,
        "reddit_subreddit_id" : self.reddit_subreddit_id,
        "subreddit_name_prefixed" : self.subreddit_name_prefixed,
        "title" : self.title,
        "gilded" : self.gilded,
        "selftext" : self.selftext,
        "approved_at_utc" : self.approved_at_utc,
        "downs" : self.downs,
        "subreddit_type" : self.subreddit_type,
        "ups" : self.ups,
        "upvote_ratio" : self.upvote_ratio,
        "permalink" : self.permalink
        }
    
    
    