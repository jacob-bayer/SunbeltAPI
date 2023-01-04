# -*- coding: utf-8 -*-

from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Identity, Index, Integer, Text, text


class Subreddit(db.Model):
    __tablename__ = 'subreddits'
    __table_args__ = {'schema': 'subreddits'}

    zen_subreddit_id = Column(BigInteger, primary_key=True, index=True)
    reddit_subreddit_id = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    display_name_prefixed = Column(Text)
    title = Column(Text)
    display_name = Column(Text)
    created = Column(Float(53))
    lang = Column(Text)
    created_utc = Column(Float(53))
    path = Column(Text)
    is_enrolled_in_new_modmail = Column(Text)

    post = relationship('Post', back_populates='zen_subreddit')

    def to_dict(self):
        pass
        
class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'posts'}

    zen_post_id = Column(BigInteger, primary_key=True, index=True)
    zen_subreddit_id = Column(ForeignKey('subreddits.subreddits.zen_subreddit_id'), nullable=False)
    zen_account_id = Column(BigInteger)
    reddit_post_id = Column(Text, nullable=False)
    reddit_subreddit_id = Column(Text, nullable=False)
    reddit_account_id = Column(Text)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    approved_at_utc = Column(Text)
    permalink = Column(Text)
    thumbnail_height = Column(BigInteger)
    author_cakeday = Column(Text)
    thumbnail_width = Column(BigInteger)
    author_flair_template_id = Column(Text)
    is_reddit_media_domain = Column(Boolean)
    is_created_from_ads_ui = Column(Boolean)
    post_hint = Column(Text)
    created = Column(Float(53))
    domain = Column(Text)
    no_follow = Column(Boolean)
    created_utc = Column(Float(53))
    is_video = Column(Boolean)

    zen_subreddit = relationship('Subreddit', back_populates='post')
    post_version = relationship('PostVersion', back_populates='zen_post')

    def __repr__(self):
        return f"ZenPost({self.reddit_post_id})"
    
    def to_dict(self):
        return {
        "zen_post_id" : self.zen_post_id,
        "created_at" : str(self.created_at.strftime('%d-%m-%Y %H:%M:%S')),
        "reddit_post_id" : self.reddit_post_id,
        "reddit_account_id" : self.reddit_account_id,
        "reddit_subreddit_id" : self.reddit_subreddit_id,
        "subreddit_name_prefixed" : self.subreddit_name_prefixed,
        "title" : self.title,
        "permalink" : self.permalink
        }
    
    def most_recent_details(self):
        pass
        
    
class PostVersion(db.Model):
    __tablename__ = 'post_versions'
    __table_args__ = (
        Index('ix_posts_post_versions', 'zen_post_id', 'zen_post_version_id', 'zen_post_detail_id'),
        {'schema': 'posts'}
    )

    zen_post_id = Column(ForeignKey('posts.posts.zen_post_id'), primary_key=True, nullable=False)
    zen_post_version_id = Column(BigInteger, primary_key=True, nullable=False)
    zen_post_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))

    zen_post = relationship('Post', back_populates='post_version')
        

class PostDetail(PostVersion):
    __tablename__ = 'post_details'
    __table_args__ = {'schema': 'posts'}

    zen_post_detail_id = Column(ForeignKey('posts.post_versions.zen_post_detail_id'), primary_key=True, index=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    gilded = Column(BigInteger)
    selftext = Column(Text)
    downs = Column(BigInteger)
    ups = Column(BigInteger)
    upvote_ratio = Column(Float(53))
    num_comments = Column(BigInteger)
    num_reports = Column(Text)
    author_has_subscribed = Column(Boolean)
    author_is_mod = Column(Boolean)
    comment_limit = Column(BigInteger)
    comment_sort = Column(Text)
    parent_whitelist_status = Column(Text)
    stickied = Column(Boolean)
    subreddit_subscribers = Column(BigInteger)
    num_crossposts = Column(BigInteger)
    total_awards_received = Column(BigInteger)
    score = Column(BigInteger)
    author_premium = Column(Boolean)
    edited = Column(BigInteger)
    saved = Column(Boolean)
    mod_reason_title = Column(Text)
    clicked = Column(Boolean)
    hidden = Column(Boolean)
    pwls = Column(BigInteger)
    link_flair_css_class = Column(Text)
    top_awarded_type = Column(Text)
    hide_score = Column(Boolean)
    quarantine = Column(Boolean)
    link_flair_text_color = Column(Text)
    author_flair_background_color = Column(Text)
    is_original_content = Column(Boolean)
    is_meta = Column(Boolean)
    category = Column(Text)
    link_flair_text = Column(Text)
    can_mod_post = Column(Boolean)
    approved_by = Column(Text)
    thumbnail = Column(Text)
    author_flair_css_class = Column(Text)
    is_self = Column(Boolean)
    mod_note = Column(Text)
    link_flair_type = Column(Text)
    num_duplicates = Column(Integer)
    wls = Column(BigInteger)
    removed_by_category = Column(Text)
    banned_by = Column(Text)
    author_flair_type = Column(Text)
    allow_live_comments = Column(Boolean)
    selftext_html = Column(Text)
    likes = Column(Text)
    suggested_sort = Column(Text)
    banned_at_utc = Column(Text)
    url_overridden_by_dest = Column(Text)
    view_count = Column(Text)
    archived = Column(Boolean)
    is_crosspostable = Column(Boolean)
    pinned = Column(Boolean)
    over_18 = Column(Boolean)
    media_only = Column(Boolean)
    can_gild = Column(Boolean)
    spoiler = Column(Boolean)
    locked = Column(Boolean)
    author_flair_text = Column(Text)
    visited = Column(Boolean)
    removed_by = Column(Text)
    distinguished = Column(Text)
    mod_reason_by = Column(Text)
    removal_reason = Column(Text)
    link_flair_background_color = Column(Text)
    is_robot_indexable = Column(Boolean)
    report_reasons = Column(Text)
    discussion_type = Column(Text)
    send_replies = Column(Boolean)
    whitelist_status = Column(Text)
    contest_mode = Column(Boolean)
    author_patreon_flair = Column(Boolean)
    author_flair_text_color = Column(Text)
    link_flair_template_id = Column(Text)

    awarding = relationship('Awarding', back_populates='zen_post_detail')
    gilding = relationship('Gilding', back_populates='zen_post_detail')
    media = relationship('Media', back_populates='zen_post_detail')
    media_embed = relationship('MediaEmbed', back_populates='zen_post_detail')
    secure_media = relationship('SecureMedia', back_populates='zen_post_detail')

    def to_dict(self):
        return {
        "zen_post_detail_id" : self.zen_post_detail_id,
        "created_at" : str(self.created_at.strftime('%d-%m-%Y %H:%M:%S')),
        "gilded" : self.gilded,
        "selftext" : self.selftext,
        "approved_at_utc" : self.approved_at_utc,
        "downs" : self.downs,
        "ups" : self.ups,
        "upvote_ratio" : self.upvote_ratio
        }
    

class Awarding(db.Model):
    __tablename__ = 'awardings'
    __table_args__ = {'schema': 'posts'}

    zen_awarding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
    zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    reddit_subreddit_id = Column(Text)
    giver_coin_reward = Column(Text)
    is_new = Column(Boolean)
    days_of_drip_extension = Column(Float(53))
    coin_price = Column(BigInteger)
    id = Column(Text)
    penny_donate = Column(Text)
    coin_reward = Column(BigInteger)
    icon_url = Column(Text)
    days_of_premium = Column(Float(53))
    icon_height = Column(BigInteger)
    icon_width = Column(BigInteger)
    static_icon_width = Column(BigInteger)
    start_date = Column(Float(53))
    is_enabled = Column(Boolean)
    awardings_required_to_grant_benefits = Column(Float(53))
    description = Column(Text)
    end_date = Column(Float(53))
    sticky_duration_seconds = Column(Text)
    subreddit_coin_reward = Column(BigInteger)
    count = Column(BigInteger)
    static_icon_height = Column(BigInteger)
    name = Column(Text)
    icon_format = Column(Text)
    award_sub_type = Column(Text)
    penny_price = Column(Float(53))
    award_type = Column(Text)
    static_icon_url = Column(Text)
    zen_modified_at = Column(DateTime)

    zen_post_detail = relationship('PostDetail', back_populates='awarding')


class Gilding(db.Model):
    __tablename__ = 'gildings'
    __table_args__ = {'schema': 'posts'}

    zen_gilding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
    zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    reddit_gid = Column(Text)
    value = Column(BigInteger)
    zen_modified_at = Column(DateTime)

    zen_post_detail = relationship('PostDetail', back_populates='gilding')


class Media(db.Model):
    __tablename__ = 'media'
    __table_args__ = {'schema': 'posts'}

    zen_media_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
    zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    media_type = Column(Text)
    oembed_provider_url = Column(Text)
    oembed_version = Column(Text)
    oembed_title = Column(Text)
    oembed_type = Column(Text)
    oembed_thumbnail_width = Column(Float(53))
    oembed_height = Column(Float(53))
    oembed_width = Column(Float(53))
    oembed_html = Column(Text)
    oembed_author_name = Column(Text)
    oembed_provider_name = Column(Text)
    oembed_thumbnail_url = Column(Text)
    oembed_thumbnail_height = Column(Float(53))
    oembed_author_url = Column(Text)
    reddit_video_fallback_url = Column(Text)
    reddit_video_bitrate_kbps = Column(Float(53))
    reddit_video_height = Column(Float(53))
    reddit_video_width = Column(Float(53))
    reddit_video_scrubber_media_url = Column(Text)
    reddit_video_dash_url = Column(Text)
    reddit_video_duration = Column(Float(53))
    reddit_video_hls_url = Column(Text)
    reddit_video_is_gif = Column(Boolean)
    reddit_video_transcoding_status = Column(Text)
    zen_modified_at = Column(DateTime)

    zen_post_detail = relationship('PostDetail', back_populates='media')


class MediaEmbed(db.Model):
    __tablename__ = 'media_embed'
    __table_args__ = {'schema': 'posts'}

    zen_media_embed_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
    zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    content = Column(Text)
    width = Column(Float(53))
    scrolling = Column(Boolean)
    height = Column(Float(53))
    zen_modified_at = Column(DateTime)

    zen_post_detail = relationship('PostDetail', back_populates='media_embed')


class SecureMedia(db.Model):
    __tablename__ = 'secure_media'
    __table_args__ = {'schema': 'posts'}

    zen_secure_media_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
    zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    type = Column(Text)
    oembed_provider_url = Column(Text)
    oembed_version = Column(Text)
    oembed_title = Column(Text)
    oembed_type = Column(Text)
    oembed_thumbnail_width = Column(Float(53))
    oembed_height = Column(Float(53))
    oembed_width = Column(Float(53))
    oembed_html = Column(Text)
    oembed_author_name = Column(Text)
    oembed_provider_name = Column(Text)
    oembed_thumbnail_url = Column(Text)
    oembed_thumbnail_height = Column(Float(53))
    oembed_author_url = Column(Text)
    reddit_video_bitrate_kbps = Column(Float(53))
    reddit_video_fallback_url = Column(Text)
    reddit_video_height = Column(Float(53))
    reddit_video_width = Column(Float(53))
    reddit_video_scrubber_media_url = Column(Text)
    reddit_video_dash_url = Column(Text)
    reddit_video_duration = Column(Float(53))
    reddit_video_hls_url = Column(Text)
    reddit_video_is_gif = Column(Boolean)
    reddit_video_transcoding_status = Column(Text)
    zen_modified_at = Column(DateTime)

    zen_post_detail = relationship('PostDetail', back_populates='secure_media')
    
