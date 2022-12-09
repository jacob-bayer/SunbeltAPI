# -*- coding: utf-8 -*-
#from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Identity, Integer, Text, text
from app import db
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'posts'}

    post_id = db.Column(db.BigInteger, primary_key=True, index=True)
    modified_at = db.Column(db.DateTime, nullable=False)
    #created_at = db.Column(db.DateTime, nullable=False, server_default=text('now()'))
    reddit_post_id = db.Column(db.Text)
    reddit_account_id = db.Column(db.Text)
    reddit_subreddit_id = db.Column(db.Text)
    subreddit_name_prefixed = db.Column(db.Text)
    title = db.Column(db.Text)
    gilded = db.Column(db.BigInteger)
    selftext = db.Column(db.Text)
    approved_at_utc = db.Column(db.Text)
    downs = db.Column(db.BigInteger)
    subreddit_type = db.Column(db.Text)
    ups = db.Column(db.BigInteger)
    upvote_ratio = db.Column(db.Float(53))
    permalink = db.Column(db.Text)

   
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
    
    
    