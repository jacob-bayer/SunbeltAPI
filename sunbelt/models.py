# -*- coding: utf-8 -*-

from sunbelt import db
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Identity, Index, Integer, Text, text, Numeric

# used for sorting by properties
# https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html
from sqlalchemy.ext.hybrid import hybrid_property


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

    posts = relationship('Post', back_populates='subreddit')
    versions = relationship('SubredditVersion', back_populates='subreddit')

    @hybrid_property
    def reddit_unique_id(self):
        return self.reddit_subreddit_id

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_subreddit_id

    @property
    def most_recent_detail(self):
        return self.versions[-1].detail

    def to_dict(self):
        main_dict = {
            'zen_subreddit_id': self.zen_subreddit_id,
            'reddit_unique_id' : self.reddit_unique_id,
            'zen_unique_id' : self.zen_unique_id,
            'reddit_subreddit_id': self.reddit_subreddit_id,
            'url': self.url,
            'zen_created_at': self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'display_name_prefixed': self.display_name_prefixed,
            'title': self.title,
            'display_name': self.display_name,
            'created': self.created,
            'lang': self.lang,
            'created_utc': self.created_utc,
        }
        most_recent_details_dict = {'most_recent_' + key: value for key, value in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_details_dict}
    

class SubredditVersion(db.Model):
    __tablename__ = 'subreddit_versions'
    __table_args__ = (
        Index('ix_subreddits_subreddit_versions', 'zen_subreddit_id', 'zen_subreddit_version_id', 'zen_subreddit_detail_id'),
        {'schema': 'subreddits'}
    )

    zen_subreddit_id = Column(ForeignKey('subreddits.subreddits.zen_subreddit_id'), primary_key=True, nullable=False)
    zen_subreddit_version_id = Column(BigInteger, primary_key=True, nullable=False)
    zen_subreddit_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))

    subreddit = relationship('Subreddit', back_populates='versions')
    detail = relationship('SubredditDetail', uselist = False, back_populates='version')

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_subreddit_id

    @hybrid_property
    def zen_version_id(self):
        return self.zen_subreddit_version_id

class SubredditDetail(db.Model):
    __tablename__ = 'subreddit_details'
    __table_args__ = {'schema': 'subreddits'}

    zen_subreddit_detail_id = Column(ForeignKey('subreddits.subreddit_versions.zen_subreddit_detail_id'), primary_key=True, index=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    active_user_count = Column(BigInteger)
    accounts_active = Column(BigInteger)
    public_traffic = Column(Boolean)
    subscribers = Column(BigInteger)
    subreddit_type = Column(Text)
    suggested_comment_sort = Column(Text)
    allow_polls = Column(Boolean)
    collapse_deleted_comments = Column(Boolean)
    public_description_html = Column(Text)
    allow_videos = Column(Boolean)
    allow_discovery = Column(Boolean)
    accept_followers = Column(Boolean)
    is_crosspostable_subreddit = Column(Boolean)
    notification_level = Column(Text)
    should_show_media_in_comments_setting = Column(Boolean)
    user_flair_background_color = Column(Text)
    submit_text_html = Column(Text)
    restrict_posting = Column(Boolean)
    free_form_reports = Column(Boolean)
    wiki_enabled = Column(Boolean)
    header_img = Column(Text)
    allow_galleries = Column(Boolean)
    primary_color = Column(Text)
    icon_img = Column(Text)
    quarantine = Column(Boolean)
    hide_ads = Column(Boolean)
    prediction_leaderboard_entry_type = Column(Text)
    emojis_enabled = Column(Boolean)
    advertiser_category = Column(Text)
    public_description = Column(Text)
    comment_score_hide_mins = Column(BigInteger)
    allow_predictions = Column(Boolean)
    community_icon = Column(Text)
    banner_background_image = Column(Text)
    original_content_tag_enabled = Column(Boolean)
    community_reviewed = Column(Boolean)
    submit_text = Column(Text)
    description_html = Column(Text)
    spoilers_enabled = Column(Boolean)
    allow_talks = Column(Boolean)
    all_original_content = Column(Boolean)
    has_menu_widget = Column(Boolean)
    key_color = Column(Text)
    wls = Column(BigInteger)
    show_media_preview = Column(Boolean)
    submission_type = Column(Text)
    allow_videogifs = Column(Boolean)
    should_archive_posts = Column(Boolean)
    can_assign_link_flair = Column(Boolean)
    accounts_active_is_fuzzed = Column(Boolean)
    allow_prediction_contributors = Column(Boolean)
    submit_text_label = Column(Text)
    link_flair_position = Column(Text)
    allow_chat_post_creation = Column(Boolean)
    user_sr_theme_enabled = Column(Boolean)
    link_flair_enabled = Column(Boolean)
    disable_contributor_requests = Column(Boolean)
    banner_img = Column(Text)
    content_category = Column(Text)
    banner_background_color = Column(Text)
    show_media = Column(Boolean)
    over18 = Column(Boolean)
    header_title = Column(Text)
    description = Column(Text)
    is_chat_post_feature_enabled = Column(Boolean)
    submit_link_label = Column(Text)
    restrict_commenting = Column(Boolean)
    allow_images = Column(Boolean)
    whitelist_status = Column(Text)
    mobile_banner_image = Column(Text)
    allow_predictions_tournament = Column(Boolean)
    videostream_links_count = Column(Float(53))

    version = relationship('SubredditVersion', back_populates='detail')

    @hybrid_property
    def zen_detail_id(self):
        return self.zen_subreddit_detail_id

    def to_dict(self):
        return {
            'zen_subreddit_detail_id': self.zen_subreddit_detail_id,
            "zen_detail_id" : self.zen_subreddit_detail_id,
            "zen_version_id" : self.version.zen_subreddit_version_id,
            "zen_unique_id" : self.version.subreddit.zen_subreddit_id,
            'zen_created_at': self.zen_created_at,
            'active_user_count': self.active_user_count,
            'accounts_active': self.accounts_active,
            'public_traffic': self.public_traffic,
            'subscribers': self.subscribers,
            'subreddit_type': self.subreddit_type,
            'suggested_comment_sort': self.suggested_comment_sort,
            'allow_polls': self.allow_polls,
            'collapse_deleted_comments': self.collapse_deleted_comments,
            'public_description_html': self.public_description_html,
            'allow_videos': self.allow_videos,
            'allow_discovery': self.allow_discovery,
            'accept_followers': self.accept_followers,
            'is_crosspostable_subreddit': self.is_crosspostable_subreddit,
            'notification_level': self.notification_level,
            'should_show_media_in_comments_setting': self.should_show_media_in_comments_setting,
            'user_flair_background_color': self.user_flair_background_color,
            'submit_text_html': self.submit_text_html,
            'restrict_posting': self.restrict_posting,
            'free_form_reports': self.free_form_reports,
            'wiki_enabled': self.wiki_enabled,
            'header_img': self.header_img,
            'allow_galleries': self.allow_galleries,
            'primary_color': self.primary_color,
            'icon_img': self.icon_img,
            'quarantine': self.quarantine,
            'hide_ads': self.hide_ads,
            'prediction_leaderboard_entry_type': self.prediction_leaderboard_entry_type,
            'emojis_enabled': self.emojis_enabled,
            'advertiser_category': self.advertiser_category,
            'public_description': self.public_description,
            'comment_score_hide_mins': self.comment_score_hide_mins,
            'allow_predictions': self.allow_predictions,
            'community_icon': self.community_icon,
            'banner_background_image': self.banner_background_image,
            'original_content_tag_enabled': self.original_content_tag_enabled,
            'community_reviewed': self.community_reviewed,
            'submit_text': self.submit_text,
            'description_html': self.description_html,
            'spoilers_enabled': self.spoilers_enabled,
            'allow_talks': self.allow_talks,
            'all_original_content': self.all_original_content
        }


class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'posts'}

    zen_post_id = Column(BigInteger, primary_key=True, index=True)
    zen_subreddit_id = Column(BigInteger, ForeignKey('subreddits.subreddits.zen_subreddit_id'), nullable=False)
    zen_account_id = Column(BigInteger, ForeignKey('accounts.accounts.zen_account_id'))
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

    subreddit = relationship('Subreddit', back_populates='posts')
    author = relationship('Account', back_populates='posts')
    versions = relationship('PostVersion', back_populates='post')

    @hybrid_property
    def reddit_unique_id(self):
        return self.reddit_post_id

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_post_id

    def __repr__(self):
        return f"ZenPost({self.zen_post_id})"
    
    def to_dict(self):
        main_dict = {
            "zen_post_id" : self.zen_post_id,
            "zen_created_at" : self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            "reddit_post_id" : self.reddit_post_id,
            "reddit_account_id" : self.reddit_account_id,
            "reddit_subreddit_id" : self.reddit_subreddit_id,
            'reddit_unique_id' : self.reddit_unique_id,
            'zen_unique_id' : self.zen_unique_id,
            "title" : self.title,
            "permalink" : self.permalink,
            "author" : self.author.to_dict() if self.author else None,
            "versions" : [v.detail.to_dict() for v in self.versions],
            "subreddit" : self.subreddit.to_dict()
        }
        most_recent_details_dict = {'most_recent_' + k: v for k, v in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_details_dict}
    
    @property
    def most_recent_detail(self):
        return self.versions[-1].detail



    # This works but the init_on_load function conflicts with author for some reason
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.init_on_load()


    # @reconstructor
    # def init_on_load(self):
    #     mr_vars = vars(self.most_recent_detail)
    #     for var, value in mr_vars.items():
    #         setattr(self, var, value)

        
    
class PostVersion(db.Model):
    __tablename__ = 'post_versions'
    __table_args__ = (
        Index('ix_posts_post_versions', 'zen_post_id', 'zen_post_version_id', 'zen_post_detail_id'),
        {'schema': 'posts'}
    )

    zen_post_id = Column(BigInteger, ForeignKey('posts.posts.zen_post_id'), primary_key=True, nullable=False)
    zen_post_version_id = Column(BigInteger, primary_key=True, nullable=False)
    zen_post_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))

    post = relationship('Post', back_populates='versions')
    detail = relationship('PostDetail', uselist=False, back_populates='version')

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_post_id

    @hybrid_property
    def zen_version_id(self):
        return self.zen_post_version_id


class PostDetail(db.Model):
    __tablename__ = 'post_details'
    __table_args__ = {'schema': 'posts'}

    zen_post_detail_id = Column(BigInteger, ForeignKey('posts.post_versions.zen_post_detail_id'), primary_key=True, index=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    gilded = Column(BigInteger)
    selftext = Column(Text)
    downs = Column(BigInteger)
    ups = Column(BigInteger)
    upvote_ratio = Column(Float(53))
    num_comments = Column(BigInteger)
    num_reports = Column(Text)
    removed = Column(Boolean, nullable=False)
    deleted = Column(Boolean, nullable=False)
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

    # awardings = relationship('PostAwarding', back_populates='detail')
    # gildings = relationship('PostGilding', back_populates='detail')
    # media = relationship('PostMedia', back_populates='detail')
    # media_embeds = relationship('PostMediaEmbed', back_populates='detail')
    # secure_media = relationship('PostSecureMedia', back_populates='detail')

    version = relationship('PostVersion', back_populates='detail')

    @hybrid_property
    def zen_detail_id(self):
        return self.zen_post_detail_id

    def to_dict(self):
        return {
        "zen_post_detail_id" : self.zen_post_detail_id,
        "zen_post_version_id" : self.version.zen_post_version_id,
        "zen_post_id" : self.version.post.zen_post_id,
        "zen_detail_id" : self.zen_post_detail_id,
        "zen_version_id" : self.version.zen_post_version_id,
        "zen_unique_id" : self.version.post.zen_post_id,
        "zen_created_at" : self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
        "gilded" : self.gilded,
        "selftext" : self.selftext,
        "downs" : self.downs,
        "ups" : self.ups,
        "upvote_ratio" : self.upvote_ratio
        }
    

# class PostAwarding(db.Model):
#     __tablename__ = 'awardings'
#     __table_args__ = {'schema': 'posts'}

#     zen_awarding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     reddit_subreddit_id = Column(Text)
#     giver_coin_reward = Column(Text)
#     is_new = Column(Boolean)
#     days_of_drip_extension = Column(Float(53))
#     coin_price = Column(BigInteger)
#     id = Column(Text)
#     penny_donate = Column(Text)
#     coin_reward = Column(BigInteger)
#     icon_url = Column(Text)
#     days_of_premium = Column(Float(53))
#     icon_height = Column(BigInteger)
#     icon_width = Column(BigInteger)
#     static_icon_width = Column(BigInteger)
#     start_date = Column(Float(53))
#     is_enabled = Column(Boolean)
#     awardings_required_to_grant_benefits = Column(Float(53))
#     description = Column(Text)
#     end_date = Column(Float(53))
#     sticky_duration_seconds = Column(Text)
#     subreddit_coin_reward = Column(BigInteger)
#     count = Column(BigInteger)
#     static_icon_height = Column(BigInteger)
#     name = Column(Text)
#     icon_format = Column(Text)
#     award_sub_type = Column(Text)
#     penny_price = Column(Float(53))
#     award_type = Column(Text)
#     static_icon_url = Column(Text)

#     detail = relationship('PostDetail', back_populates='awardings')


# class PostGilding(db.Model):
#     __tablename__ = 'gildings'
#     __table_args__ = {'schema': 'posts'}

#     zen_gilding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_post_detail_id = Column(BigInteger, ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     reddit_gid = Column(Text)
#     value = Column(BigInteger)

#     detail = relationship('PostDetail', back_populates='gildings')


# class PostMedia(db.Model):
#     __tablename__ = 'media'
#     __table_args__ = {'schema': 'posts'}

#     zen_media_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_post_detail_id = Column(BigInteger, ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     media_type = Column(Text)
#     oembed_provider_url = Column(Text)
#     oembed_version = Column(Text)
#     oembed_title = Column(Text)
#     oembed_type = Column(Text)
#     oembed_thumbnail_width = Column(Float(53))
#     oembed_height = Column(Float(53))
#     oembed_width = Column(Float(53))
#     oembed_html = Column(Text)
#     oembed_author_name = Column(Text)
#     oembed_provider_name = Column(Text)
#     oembed_thumbnail_url = Column(Text)
#     oembed_thumbnail_height = Column(Float(53))
#     oembed_author_url = Column(Text)
#     reddit_video_fallback_url = Column(Text)
#     reddit_video_bitrate_kbps = Column(Float(53))
#     reddit_video_height = Column(Float(53))
#     reddit_video_width = Column(Float(53))
#     reddit_video_scrubber_media_url = Column(Text)
#     reddit_video_dash_url = Column(Text)
#     reddit_video_duration = Column(Float(53))
#     reddit_video_hls_url = Column(Text)
#     reddit_video_is_gif = Column(Boolean)
#     reddit_video_transcoding_status = Column(Text)

#     detail = relationship('PostDetail', back_populates='media')


# class PostMediaEmbed(db.Model):
#     __tablename__ = 'media_embed'
#     __table_args__ = {'schema': 'posts'}

#     zen_media_embed_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     content = Column(Text)
#     width = Column(Float(53))
#     scrolling = Column(Boolean)
#     height = Column(Float(53))

#     detail = relationship('PostDetail', back_populates='media_embeds')


# class PostSecureMedia(db.Model):
#     __tablename__ = 'secure_media'
#     __table_args__ = {'schema': 'posts'}

#     zen_secure_media_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_post_detail_id = Column(ForeignKey('posts.post_details.zen_post_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     type = Column(Text)
#     oembed_provider_url = Column(Text)
#     oembed_version = Column(Text)
#     oembed_title = Column(Text)
#     oembed_type = Column(Text)
#     oembed_thumbnail_width = Column(Float(53))
#     oembed_height = Column(Float(53))
#     oembed_width = Column(Float(53))
#     oembed_html = Column(Text)
#     oembed_author_name = Column(Text)
#     oembed_provider_name = Column(Text)
#     oembed_thumbnail_url = Column(Text)
#     oembed_thumbnail_height = Column(Float(53))
#     oembed_author_url = Column(Text)
#     reddit_video_bitrate_kbps = Column(Float(53))
#     reddit_video_fallback_url = Column(Text)
#     reddit_video_height = Column(Float(53))
#     reddit_video_width = Column(Float(53))
#     reddit_video_scrubber_media_url = Column(Text)
#     reddit_video_dash_url = Column(Text)
#     reddit_video_duration = Column(Float(53))
#     reddit_video_hls_url = Column(Text)
#     reddit_video_is_gif = Column(Boolean)
#     reddit_video_transcoding_status = Column(Text)

#     detail = relationship('PostDetail', back_populates='secure_media')
    
class Account(db.Model):
    __tablename__ = 'accounts'
    __table_args__ = {'schema': 'accounts'}

    zen_account_id = Column(BigInteger, primary_key=True, index=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    name = Column(Text, nullable=False)
    reddit_account_id = Column(Text)
    created = Column(Float(53))
    created_utc = Column(Float(53))

    posts = relationship('Post', back_populates='author')
    versions = relationship('AccountVersion', back_populates='account')

    @hybrid_property
    def reddit_unique_id(self):
        return self.reddit_account_id

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_account_id

    @property
    def most_recent_detail(self):
        return self.versions[-1].detail

    def __repr__(self):
        return f'ZenAccount({self.zen_account_id})'

    def to_dict(self):
        main_dict = {
            'zen_account_id': self.zen_account_id,
            'zen_created_at': self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'name': self.name,
            'reddit_account_id': self.reddit_account_id,
            'reddit_unique_id': self.reddit_unique_id,
            'zen_unique_id': self.zen_unique_id
        }
        most_recent_detail_dict = {'most_recent_' + k: v for k, v in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_detail_dict}

class AccountVersion(db.Model):
    __tablename__ = 'account_versions'
    __table_args__ = (
        Index('ix_accounts_account_versions', 'zen_account_id', 'zen_account_version_id', 'zen_account_detail_id'),
        {'schema': 'accounts'}
    )

    zen_account_id = Column(BigInteger, ForeignKey('accounts.accounts.zen_account_id'), primary_key=True, nullable=False)
    zen_account_version_id = Column(BigInteger, primary_key=True, nullable=False)
    zen_account_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))

    account = relationship('Account', back_populates='versions')
    detail = relationship('AccountDetail', uselist = False, back_populates='version')

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_account_id

    @hybrid_property
    def zen_version_id(self):
        return self.zen_account_version_id

class AccountDetail(db.Model):
    __tablename__ = 'account_details'
    __table_args__ = {'schema': 'accounts'}

    zen_account_detail_id = Column(BigInteger, ForeignKey('accounts.account_versions.zen_account_detail_id'), unique = True, primary_key=True, index=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    comment_karma = Column(BigInteger)
    link_karma = Column(BigInteger)
    total_karma = Column(BigInteger)
    awardee_karma = Column(BigInteger)
    awarder_karma = Column(BigInteger)
    listing_use_sort = Column(Boolean)
    is_employee = Column(Boolean)
    snoovatar_size = Column(Text)
    verified = Column(Boolean)
    is_gold = Column(Boolean)
    icon_img = Column(Text)
    hide_from_robots = Column(Boolean)
    pref_show_snoovatar = Column(Boolean)
    snoovatar_img = Column(Text)
    accept_followers = Column(Boolean)
    #has_verified_email = Column(Boolean)

    version = relationship('AccountVersion', back_populates='detail')

    @hybrid_property
    def zen_detail_id(self):
        return self.zen_account_detail_id

    def to_dict(self):
        return {
            'zen_account_detail_id': self.zen_account_detail_id,
            'zen_created_at': self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'comment_karma': self.comment_karma,
            'link_karma': self.link_karma,
            'total_karma': self.total_karma,
            'awardee_karma': self.awardee_karma,
            'awarder_karma': self.awarder_karma,
            'listing_use_sort': self.listing_use_sort,
            'is_employee': self.is_employee,
            'snoovatar_size': self.snoovatar_size,
            'verified': self.verified,
            'is_gold': self.is_gold,
            'icon_img': self.icon_img,
            'hide_from_robots': self.hide_from_robots,
            'pref_show_snoovatar': self.pref_show_snoovatar,
            'snoovatar_img': self.snoovatar_img,
            'accept_followers': self.accept_followers,
            #'has_verified_email': self.has_verified_email
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    __table_args__ = {'schema': 'comments'}

    zen_comment_id = Column(BigInteger, primary_key=True, index=True)
    zen_post_id = Column(BigInteger, ForeignKey('posts.posts.zen_post_id'), nullable=False)
    zen_subreddit_id = Column(BigInteger, ForeignKey('subreddits.subreddits.zen_subreddit_id'), nullable=False)
    zen_account_id = Column(BigInteger, ForeignKey('accounts.accounts.zen_account_id'))
    reddit_comment_id = Column(Text, nullable=False)
    reddit_parent_id = Column(Text)
    reddit_post_id = Column(Text, nullable=False)
    reddit_subreddit_id = Column(Text, nullable=False)
    reddit_account_id = Column(Text)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    created_utc = Column(Numeric)
    depth = Column(BigInteger)
    permalink = Column(Text)
    is_submitter = Column(Boolean)
    created = Column(Numeric)

    author = relationship('Account')
    versions = relationship('CommentVersion', back_populates='comment')

    def __repr__(self):
        return f'ZenComment({self.zen_comment_id})'

    @property
    def parent(self):
        if self.reddit_parent_id:
            if self.reddit_parent_id.startswith('t1_'):
                return Comment.query.filter(Comment.reddit_comment_id == self.reddit_parent_id).first()
            else:
                return Post.query.filter(Post.reddit_post_id == self.reddit_parent_id).first()
        else:
            return None
    
    @hybrid_property
    def reddit_unique_id(self):
        return self.reddit_comment_id

    # allows sort by this
    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html
    @hybrid_property
    def zen_unique_id(self):
        return self.zen_comment_id

    @property
    def most_recent_detail(self):
        return self.versions[-1].detail

    def to_dict(self):
        main_dict = {
            'zen_comment_id': self.zen_comment_id,
            'zen_post_id': self.zen_post_id,
            'zen_subreddit_id': self.zen_subreddit_id,
            'zen_account_id': self.zen_account_id,
            'reddit_comment_id': self.reddit_comment_id,
            'reddit_parent_id': self.reddit_parent_id,
            'reddit_post_id': self.reddit_post_id,
            'reddit_account_id': self.reddit_account_id,
            'reddit_unique_id': self.reddit_unique_id,
            'zen_unique_id': self.zen_unique_id,
            'reddit_subreddit_id': self.reddit_subreddit_id,
            'zen_created_at': self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'created_utc': float(self.created_utc),
            'depth': str(self.depth) or '',
            'permalink': self.permalink,
            'is_submitter': self.is_submitter,
            'created': float(self.created),
            'author': self.author.to_dict() if self.author else None,
        }
        most_recent_details_dict = {'most_recent_' + k: v for k, v in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_details_dict}

class CommentVersion(db.Model):
    __tablename__ = 'comment_versions'
    __table_args__ = (
        Index('ix_comments_comment_versions', 'zen_comment_id', 'zen_comment_version_id', 'zen_comment_detail_id'),
        {'schema': 'comments'}
    )

    zen_comment_id = Column(BigInteger, ForeignKey('comments.comments.zen_comment_id'), primary_key=True, nullable=False)
    zen_comment_version_id = Column(BigInteger, primary_key=True, nullable=False)
    zen_comment_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))

    comment = relationship('Comment', back_populates='versions')
    detail = relationship('CommentDetail', uselist=False, back_populates='version')

    @hybrid_property
    def zen_unique_id(self):
        return self.zen_comment_id

    @hybrid_property
    def zen_version_id(self):
        return self.zen_comment_version_id

class CommentDetail(db.Model):
    __tablename__ = 'comment_details'
    __table_args__ = {'schema': 'comments'}

    zen_comment_detail_id = Column(ForeignKey('comments.comment_versions.zen_comment_detail_id'), primary_key=True, index=True)
    zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    controversiality = Column(BigInteger)
    ups = Column(BigInteger)
    downs = Column(BigInteger)
    score = Column(BigInteger)
    body = Column(Text)
    edited = Column(BigInteger)
    removed = Column(Boolean, nullable=False)
    deleted = Column(Boolean, nullable=False)
    author_cakeday = Column(Boolean)
    author_has_subscribed = Column(Boolean)
    author_is_mod = Column(Boolean)
    comment_type = Column(Text)
    author_flair_type = Column(Text)
    total_awards_received = Column(BigInteger)
    author_flair_template_id = Column(Text)
    mod_reason_title = Column(Text)
    gilded = Column(BigInteger)
    archived = Column(Boolean)
    collapsed_reason_code = Column(Text)
    no_follow = Column(Boolean)
    can_mod_post = Column(Boolean)
    send_replies = Column(Boolean)
    mod_note = Column(Text)
    collapsed = Column(Boolean)
    top_awarded_type = Column(Text)
    author_flair_css_class = Column(Text)
    author_patreon_flair = Column(Boolean)
    body_html = Column(Text)
    removal_reason = Column(Text)
    collapsed_reason = Column(Text)
    distinguished = Column(Text)
    associated_award = Column(Text)
    stickied = Column(Boolean)
    author_premium = Column(Boolean)
    can_gild = Column(Boolean)
    unrepliable_reason = Column(Text)
    author_flair_text_color = Column(Text)
    score_hidden = Column(Boolean)
    subreddit_type = Column(Text)
    locked = Column(Boolean)
    report_reasons = Column(Text)
    author_flair_text = Column(Text)
    author_flair_background_color = Column(Text)
    collapsed_because_crowd_control = Column(Text)

    # awardings = relationship('CommentAwarding', back_populates='detail')
    # gildings = relationship('CommentGilding', back_populates='detail')

    version = relationship('CommentVersion', back_populates='detail')

    @hybrid_property
    def zen_detail_id(self):
        return self.zen_comment_detail_id

    def to_dict(self):
        return {
            'zen_comment_detail_id': self.zen_comment_detail_id,
            "zen_comment_version_id" : self.version.zen_comment_version_id,
            "zen_detail_id" : self.zen_comment_detail_id,
            "zen_version_id" : self.version.zen_comment_version_id,
            'zen_created_at': self.zen_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'controversiality': str(self.controversiality) or '',
            'ups': self.ups,
            'downs': self.downs,
            'score': self.score,
            'body': self.body,
            'edited': self.edited,
            'author_cakeday': self.author_cakeday,
            'author_has_subscribed': self.author_has_subscribed,
            'author_is_mod': self.author_is_mod,
            'comment_type': self.comment_type,
            'author_flair_type': self.author_flair_type,
            'total_awards_received': self.total_awards_received,
            'author_flair_template_id': self.author_flair_template_id,
            'mod_reason_title': self.mod_reason_title,
            'gilded': self.gilded,
            'archived': self.archived,
            'collapsed_reason_code': self.collapsed_reason_code,
            'no_follow': self.no_follow,
            'can_mod_post': self.can_mod_post,
            'send_replies': self.send_replies,
            'mod_note': self.mod_note,
            'collapsed': self.collapsed,
            'top_awarded_type': self.top_awarded_type,
            'author_flair_css_class': self.author_flair_css_class,
            'author_patreon_flair': self.author_patreon_flair,
            'body_html': self.body_html,
            'removal_reason': self.removal_reason,
            'collapsed_reason': self.collapsed_reason,
            'distinguished': self.distinguished,
            'associated_award': self.associated_award,
            'stickied': self.stickied,
            'author_premium': self.author_premium,
            'can_gild': self.can_gild,
            'unrepliable_reason': self.unrepliable_reason,
            'author_flair_text_color': self.author_flair_text_color,
            'score_hidden': self.score_hidden,
            'subreddit_type': self.subreddit_type,
            'locked': self.locked,
            'report_reasons': self.report_reasons,
            'author_flair_text': self.author_flair_text
        }


# class CommentAwarding(db.Model):
#     __tablename__ = 'awardings'
#     __table_args__ = {'schema': 'comments'}

#     zen_awarding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_comment_detail_id = Column(ForeignKey('comments.comment_details.zen_comment_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     giver_coin_reward = Column(Text)
#     is_new = Column(Boolean)
#     days_of_drip_extension = Column(Text)
#     coin_price = Column(BigInteger)
#     penny_donate = Column(Text)
#     coin_reward = Column(BigInteger)
#     icon_url = Column(Text)
#     days_of_premium = Column(Numeric)
#     icon_height = Column(BigInteger)
#     icon_width = Column(BigInteger)
#     static_icon_width = Column(BigInteger)
#     start_date = Column(Numeric)
#     is_enabled = Column(Boolean)
#     awardings_required_to_grant_benefits = Column(Numeric)
#     description = Column(Text)
#     end_date = Column(Text)
#     sticky_duration_seconds = Column(Text)
#     subreddit_coin_reward = Column(BigInteger)
#     count = Column(BigInteger)
#     static_icon_height = Column(BigInteger)
#     name = Column(Text)
#     icon_format = Column(Text)
#     award_sub_type = Column(Text)
#     penny_price = Column(Numeric)
#     award_type = Column(Text)
#     static_icon_url = Column(Text)

#     detail = relationship('CommentDetail', back_populates='awardings')


# class CommentGilding(db.Model):
#     __tablename__ = 'gildings'
#     __table_args__ = {'schema': 'comments'}

#     zen_gilding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     zen_comment_detail_id = Column(ForeignKey('comments.comment_details.zen_comment_detail_id'), nullable=False)
#     zen_created_at = Column(DateTime, nullable=False, server_default=text('now()'))
#     reddit_gid = Column(Text)
#     value = Column(Numeric)

#     detail = relationship('CommentDetail', back_populates='gildings')
