# -*- coding: utf-8 -*-

from . import db
from sqlalchemy.orm import relationship, reconstructor, aliased
from sqlalchemy import ( BigInteger, Boolean, Column, DateTime, Float, 
                        ForeignKey, Index, Integer, Text, text, Numeric, select, desc)


# used for sorting by properties
# https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html
from sqlalchemy.ext.hybrid import hybrid_property

def col_equals(column_name, string):
    def default_function(context):
        return context.current_parameters.get(column_name) == string
    return default_function


class Subreddit(db.Model):
    __tablename__ = 'subreddits'
    __table_args__ = {'schema': 'subreddits'}

    sun_subreddit_id = Column(BigInteger, primary_key=True, index=True)
    reddit_subreddit_id = Column(Text, nullable=False, index = True)
    url = Column(Text, nullable=False)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
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
    def sun_unique_id(self):
        return self.sun_subreddit_id

    @property
    def most_recent_detail(self):
        return self.versions[-1].detail

    @hybrid_property
    def most_recent_version_updated_at(self):
        return self.versions[-1].sun_created_at

    @most_recent_version_updated_at.expression
    def most_recent_version_updated_at(cls):
        return select([SubredditVersion.sun_created_at])\
                .where(SubredditVersion.sun_subreddit_id == cls.sun_subreddit_id)\
                    .order_by(SubredditVersion.sun_created_at.desc()).limit(1).as_scalar()

    def to_dict(self):
        main_dict = {
            'sun_subreddit_id': self.sun_subreddit_id,
            'reddit_unique_id' : self.reddit_unique_id,
            'sun_unique_id' : self.sun_unique_id,
            'reddit_subreddit_id': self.reddit_subreddit_id,
            'most_recent_sun_version_id': self.versions[-1].sun_version_id,
            'most_recent_sun_detail_id': self.most_recent_detail.sun_detail_id,
            'url': self.url,
            'sun_created_at': self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'display_name_prefixed': self.display_name_prefixed,
            'title': self.title,
            'display_name': self.display_name,
            'created': self.created,
            'lang': self.lang,
            'created_utc': self.created_utc,
            'version_count': len(self.versions),
            'most_recent_version_updated_at': self.most_recent_version_updated_at.strftime('%d-%m-%Y %H:%M:%S'),
            'versons': [version.detail.to_dict() for version in self.versions],
        }
        most_recent_details_dict = {key: value for key, value in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_details_dict}
    

class SubredditVersion(db.Model):
    __tablename__ = 'subreddit_versions'
    __table_args__ = (
        Index('ix_subreddits_subreddit_versions', 'sun_subreddit_id', 'sun_subreddit_version_id', 'sun_subreddit_detail_id'),
        {'schema': 'subreddits'}
    )

    sun_subreddit_id = Column(ForeignKey(Subreddit.sun_subreddit_id), primary_key=True, index=True)
    sun_subreddit_version_id = Column(BigInteger, primary_key=True, nullable=False)
    sun_subreddit_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))

    subreddit = relationship('Subreddit', back_populates='versions')
    detail = relationship('SubredditDetail', uselist = False, back_populates='version')

    @hybrid_property
    def sun_unique_id(self):
        return self.sun_subreddit_id

    @hybrid_property
    def sun_version_id(self):
        return self.sun_subreddit_version_id

    @hybrid_property
    def sun_detail_id(self):
        return self.sun_subreddit_detail_id

    # TODO:
    # I HAVE DECIDED THAT VERSION AND DETAIL TABLES SHOULD BE MERGED
    # So that the detail has the version id
    # This will make it easier to move variables like removed, edited, deleted to the main table
    # As a workaround, the below works


    # This works here but the init_on_load function conflicts with author on main table posts/comments for some reason
    # This essentially makes the version usable as a detail

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()

    @reconstructor
    def init_on_load(self):
        if self.detail:
            detail_vars = self.detail.to_dict()
            for var, value in detail_vars.items():
                if not hasattr(self, var):
                    setattr(self, var, value)


class SubredditDetail(db.Model):
    __tablename__ = 'subreddit_details'
    __table_args__ = {'schema': 'subreddits'}

    sun_subreddit_detail_id = Column(ForeignKey(SubredditVersion.sun_subreddit_detail_id), primary_key=True, index=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
    active_user_count = Column(BigInteger)
    accounts_active = Column(BigInteger)
    public_traffic = Column(Boolean)
    subscribers = Column(BigInteger)
    subreddit_type = Column(Text)
    suggested_comment_sort = Column(Text)
    deleted = Column(Boolean, nullable=False, server_default=text('false'))
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
    def sun_detail_id(self):
        return self.sun_subreddit_detail_id

    def to_dict(self):
        return {
            'sun_subreddit_detail_id': self.sun_subreddit_detail_id,
            "sun_detail_id" : self.sun_subreddit_detail_id,
            "sun_version_id" : self.version.sun_subreddit_version_id,
            "sun_unique_id" : self.version.subreddit.sun_subreddit_id,
            'sun_created_at': self.sun_created_at,
            'active_user_count': self.active_user_count,
            'accounts_active': self.accounts_active,
            'public_traffic': self.public_traffic,
            'subscribers': self.subscribers,
            'subreddit_type': self.subreddit_type,
            'suggested_comment_sort': self.suggested_comment_sort,
            'allow_polls': self.allow_polls,
            'deleted': self.deleted,
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


class Account(db.Model):
    __tablename__ = 'accounts'
    __table_args__ = {'schema': 'accounts'}

    sun_account_id = Column(BigInteger, primary_key=True, index=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
    name = Column(Text, nullable=False)
    reddit_account_id = Column(Text, nullable=False, index=True)
    created = Column(Float(53))
    created_utc = Column(Float(53))

    posts = relationship('Post', back_populates='author')
    versions = relationship('AccountVersion', back_populates='account')

    @hybrid_property
    def reddit_unique_id(self):
        return self.reddit_account_id

    @hybrid_property
    def sun_unique_id(self):
        return self.sun_account_id

    @property
    def most_recent_detail(self):
        return self.versions[-1].detail

    @hybrid_property
    def most_recent_version_updated_at(self):
        return self.versions[-1].sun_created_at

    @most_recent_version_updated_at.expression
    def most_recent_version_updated_at(cls):
        return select([AccountVersion.sun_created_at])\
                .where(AccountVersion.sun_account_id == cls.sun_account_id)\
                    .order_by(AccountVersion.sun_created_at.desc()).limit(1).as_scalar()

    def __repr__(self):
        return f'SunAccount({self.sun_account_id})'

    def to_dict(self):
        main_dict = {
            'sun_account_id': self.sun_account_id,
            'sun_created_at': self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'name': self.name,
            'reddit_account_id': self.reddit_account_id,
            'reddit_unique_id': self.reddit_unique_id,
            'sun_unique_id': self.sun_unique_id,
            'version_count': len(self.versions),
            'most_recent_version_updated_at': self.most_recent_version_updated_at.strftime('%d-%m-%Y %H:%M:%S'),
            'versions': [v.detail.to_dict() for v in self.versions],

        }
        most_recent_detail_dict = {k: v for k, v in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_detail_dict}

class AccountVersion(db.Model):
    __tablename__ = 'account_versions'
    __table_args__ = (
        Index('ix_accounts_account_versions', 'sun_account_id', 'sun_account_version_id', 'sun_account_detail_id'),
        {'schema': 'accounts'}
    )

    sun_account_id = Column(BigInteger, ForeignKey(Account.sun_account_id), primary_key=True, nullable=False)
    sun_account_version_id = Column(BigInteger, primary_key=True, nullable=False)
    sun_account_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))

    account = relationship('Account', back_populates='versions')
    detail = relationship('AccountDetail', uselist = False, back_populates='version')

    @hybrid_property
    def sun_unique_id(self):
        return self.sun_account_id

    @hybrid_property
    def sun_version_id(self):
        return self.sun_account_version_id

    @hybrid_property
    def sun_detail_id(self):
        return self.sun_account_detail_id

    # TODO:
    # I HAVE DECIDED THAT VERSION AND DETAIL TABLES SHOULD BE MERGED
    # So that the detail has the version id
    # This will make it easier to move variables like removed, edited, deleted to the main table
    # As a workaround, the below works


    # This works here but the init_on_load function conflicts with author on main table posts/comments for some reason
    # This essentially makes the version usable as a detail

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()

    @reconstructor
    def init_on_load(self):
        if self.detail:
            detail_vars = self.detail.to_dict()
            for var, value in detail_vars.items():
                if not hasattr(self, var):
                    setattr(self, var, value)


class AccountDetail(db.Model):
    __tablename__ = 'account_details'
    __table_args__ = {'schema': 'accounts'}

    sun_account_detail_id = Column(BigInteger, ForeignKey(AccountVersion.sun_account_detail_id), unique = True, primary_key=True, index=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
    comment_karma = Column(BigInteger)
    link_karma = Column(BigInteger)
    total_karma = Column(BigInteger)
    awardee_karma = Column(BigInteger)
    awarder_karma = Column(BigInteger)
    is_suspended = Column(Boolean, nullable=False, server_default=text('false'))
    deleted = Column(Boolean, nullable=False, server_default=text('false'))
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
    def sun_detail_id(self):
        return self.sun_account_detail_id

    def to_dict(self):
        return {
            'sun_account_detail_id': self.sun_account_detail_id,
            'sun_created_at': self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'comment_karma': self.comment_karma,
            'link_karma': self.link_karma,
            'total_karma': self.total_karma,
            'awardee_karma': self.awardee_karma,
            'awarder_karma': self.awarder_karma,
            'deleted': self.deleted,
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
            'is_suspended': self.is_suspended,
            #'has_verified_email': self.has_verified_email
        }

class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'posts'}

    sun_post_id = Column(BigInteger, primary_key=True, index=True)
    sun_subreddit_id = Column(BigInteger, ForeignKey(Subreddit.sun_subreddit_id), nullable=True)
    sun_account_id = Column(BigInteger, ForeignKey(Account.sun_account_id))
    reddit_post_id = Column(Text, nullable=False, index = True)
    reddit_subreddit_id = Column(Text, nullable=False)
    reddit_account_id = Column(Text)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
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

    subreddit = relationship(Subreddit, back_populates='posts')
    author = relationship(Account, back_populates='posts')
    versions = relationship('PostVersion', back_populates='post') #, order_by='PostVersion.sun_created_at')

    #most_recent_version = relationship(PostVersion, backref=backref('all_info', order_by='ThingInfo.recorded_at')

    # https://stackoverflow.com/questions/19780178/sqlalchemy-hybrid-expression-with-relationship
    # https://stackoverflow.com/questions/40614651/correlating-a-sqlalchemy-relationship-with-an-awkward-join
    # most_recent_version_rel = relationship(A,
    #     secondary=latest_a,
    #     primaryjoin=latest_a.c.a_remote == foreign_to_a,
    #     secondaryjoin=latest_a.c.a_id == A.a_id,
    #     uselist=False, viewonly=True)


    # @hybrid_property
    # def reddit_unique_id(self):
    #     return self.reddit_post_id

    # @hybrid_property
    # def sun_unique_id(self):
    #     return self.sun_post_id

    # @hybrid_property
    # def most_recent_version(self):
    #     return self.versions[-1]

    # @most_recent_version.expression
    # def most_recent_version(cls):
    #     # returns the version with the attribute is_most_recent_version set to True
    #     return (
    #         select(PostVersion)
    #         .where(PostVersion.sun_post_id == cls.sun_post_id)
    #         .order_by(desc(PostVersion.sun_post_version_id))
    #         .limit(1)
    #         .as_scalar()
    #     )


    # @hybrid_property
    # def most_recent_detail(self):
    #     return self.versions[-1].detail

    # @most_recent_version.expression
    # def most_recent_version(cls):
    #     return (
    #         select(PostVersion)
    #         .where(PostVersion.sun_post_id == cls.sun_post_id)
    #         .order_by(desc(PostVersion.sun_post_version_id))
    #         .limit(1)
    #         .as_scalar()
    #     )
    
    # @most_recent_detail.expression
    # def most_recent_detail(cls):
    #     version = cls.most_recent_version
    #     return (
    #         select(PostDetail)
    #         .where(PostDetail.sun_post_detail_id == version.sun_post_detail_id)
    #         .limit(1)
    #         .as_scalar()
    #     )

    # @most_recent_detail.expression
    # def most_recent_detail(cls):
    #     most_recent_detail_id = select([PostVersion.sun_post_detail_id])\
    #             .where(PostVersion.sun_post_id == cls.sun_post_id)\
    #                 .order_by(PostVersion.sun_post_version_id.desc()\
    #                     ).limit(1).subquery()

    #     all_postdetail_columns = [x for x in PostDetail.__table__.columns]

    #     return select(all_postdetail_columns)\
    #             .select_from(PostDetail.__table__.join(most_recent_detail_id,
    #                          PostDetail.sun_post_detail_id == most_recent_detail_id.c.sun_post_detail_id))

    # @hybrid_property
    # def most_recent_version_updated_at(self):
    #     return self.versions[-1].sun_created_at

    # @most_recent_version_updated_at.expression
    # def most_recent_version_updated_at(cls):
    #     return select([PostVersion.sun_created_at])\
    #             .where(PostVersion.sun_post_id == cls.sun_post_id)\
    #                 .order_by(PostVersion.sun_created_at.desc()).limit(1).as_scalar()

    def __repr__(self):
        return f"SunPost({self.sun_post_id})"
    
    @property
    def comments(self):
        return [c.to_dict() for c in self.comments]

    def to_dict(self):
        main_dict = {
            "sun_post_id" : self.sun_post_id,
            "sun_account_id" : self.sun_account_id,
            "sun_subreddit_id" : self.sun_subreddit_id,
            "sun_created_at" : self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'most_recent_sun_version_id': self.versions[-1].sun_version_id,
            'most_recent_sun_detail_id': self.most_recent_detail.sun_detail_id,
            "reddit_post_id" : self.reddit_post_id,
            "reddit_account_id" : self.reddit_account_id,
            "reddit_subreddit_id" : self.reddit_subreddit_id,
            'reddit_unique_id' : self.reddit_unique_id,
            'sun_unique_id' : self.sun_unique_id,
            "title" : self.title,
            "permalink" : self.permalink,
            "author" : self.author.to_dict() if self.author else None,
            "versions" : [v.detail.to_dict() for v in self.versions],
            "subreddit" : self.subreddit.to_dict() if self.subreddit else None,
            "removed" : any([version.removed for version in self.versions]),
            "edited" : any([version.edited for version in self.versions]),
            "deleted" : any([version.deleted for version in self.versions]),
            "version_count" : len(self.versions),
            'most_recent_version_updated_at': self.most_recent_version_updated_at.strftime('%d-%m-%Y %H:%M:%S'),
        }
        most_recent_details_dict = {k: v for k, v in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_details_dict}
    


    #This works but the init_on_load function conflicts with author for some reason
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.init_on_load()


    # @reconstructor
    # def init_on_load(self):
    #     mr_vars = vars(self.most_recent_detail)
    #     for var, value in mr_vars.items():
    #         setattr(self, var, value)



class PostVersion(Post):
    __tablename__ = 'post_details'
    __table_args__ = {'schema': 'posts'}

    sun_post_detail_id = Column(BigInteger,  primary_key=True, index=True)
    sun_post_version_id = Column(BigInteger, nullable=False)
    sun_post_id = Column(BigInteger, ForeignKey(Post.sun_post_id), nullable=False)
    version_updated_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
    gilded = Column(BigInteger)
    selftext = Column(Text)
    downs = Column(BigInteger)
    ups = Column(BigInteger)
    upvote_ratio = Column(Float(53))
    num_comments = Column(BigInteger)
    num_reports = Column(Text)
    removed = Column(Boolean, nullable=False, default=col_equals('selftext', '[removed]'))
    deleted = Column(Boolean, nullable=False, default=col_equals('selftext', '[deleted]'))
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
    source_is_pushshift = Column(Boolean, nullable=False, server_default=text('false'))

    # awardings = relationship('PostAwarding', back_populates='detail')
    # gildings = relationship('PostGilding', back_populates='detail')
    # media = relationship('PostMedia', back_populates='detail')
    # media_embeds = relationship('PostMediaEmbed', back_populates='detail')
    # secure_media = relationship('PostSecureMedia', back_populates='detail')

    post = relationship('Post', back_populates='versions')

    @hybrid_property
    def sun_detail_id(self):
        return self.sun_post_detail_id

    def to_dict(self):
        return {
        "sun_post_detail_id" : self.sun_post_detail_id,
        "sun_post_version_id" : self.version.sun_post_version_id,
        "sun_post_id" : self.version.post.sun_post_id,
        "sun_detail_id" : self.sun_post_detail_id,
        "sun_version_id" : self.version.sun_post_version_id,
        "sun_unique_id" : self.version.post.sun_post_id,
        "sun_created_at" : self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
        "gilded" : self.gilded,
        "selftext" : self.selftext,
        "downs" : self.downs,
        "ups" : self.ups,
        "upvote_ratio" : self.upvote_ratio,
        "num_comments" : self.num_comments,
        "deleted" : self.deleted,
        "author_has_subscribed" : self.author_has_subscribed,
        "author_is_mod" : self.author_is_mod,
        "edited" : self.edited,
        "removed" : self.removed,
        }
    

# class PostAwarding(db.Model):
#     __tablename__ = 'awardings'
#     __table_args__ = {'schema': 'public'}

#     sun_awarding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_post_detail_id = Column(ForeignKey('post_details.sun_post_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
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
#     __table_args__ = {'schema': 'public'}

#     sun_gilding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_post_detail_id = Column(BigInteger, ForeignKey('post_details.sun_post_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
#     reddit_gid = Column(Text)
#     value = Column(BigInteger)

#     detail = relationship('PostDetail', back_populates='gildings')


# class PostMedia(db.Model):
#     __tablename__ = 'media'
#     __table_args__ = {'schema': 'public'}

#     sun_media_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_post_detail_id = Column(BigInteger, ForeignKey('post_details.sun_post_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
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
#     __table_args__ = {'schema': 'public'}

#     sun_media_embed_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_post_detail_id = Column(ForeignKey('post_details.sun_post_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
#     content = Column(Text)
#     width = Column(Float(53))
#     scrolling = Column(Boolean)
#     height = Column(Float(53))

#     detail = relationship('PostDetail', back_populates='media_embeds')


# class PostSecureMedia(db.Model):
#     __tablename__ = 'secure_media'
#     __table_args__ = {'schema': 'public'}

#     sun_secure_media_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_post_detail_id = Column(ForeignKey('post_details.sun_post_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
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
    

class Comment(db.Model):
    __tablename__ = 'comments'
    __table_args__ = {'schema': 'comments'}

    sun_comment_id = Column(BigInteger, primary_key=True, index=True)
    sun_post_id = Column(BigInteger, ForeignKey(Post.sun_post_id), nullable=True) 
    sun_subreddit_id = Column(BigInteger, ForeignKey(Subreddit.sun_subreddit_id), nullable=True)
    sun_account_id = Column(BigInteger, ForeignKey(Account.sun_account_id))
    reddit_comment_id = Column(Text, nullable=False, index=True)
    reddit_parent_id = Column(Text)
    reddit_post_id = Column(Text, nullable=False)
    reddit_subreddit_id = Column(Text, nullable=False)
    reddit_account_id = Column(Text)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
    created_utc = Column(Numeric)
    depth = Column(BigInteger)
    permalink = Column(Text)
    is_submitter = Column(Boolean)
    created = Column(Numeric)

    author = relationship('Account')
    versions = relationship('CommentVersion', back_populates='comment')
    post = relationship('Post')
    subreddit = relationship('Subreddit')

    def __repr__(self):
        return f'SunComment({self.sun_comment_id})'

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
    def sun_unique_id(self):
        return self.sun_comment_id

    @property
    def most_recent_detail(self):
        return self.versions[-1].detail

    @hybrid_property
    def most_recent_version_updated_at(self):
        return self.versions[-1].sun_created_at

    @most_recent_version_updated_at.expression
    def most_recent_version_updated_at(cls):
        return select([CommentVersion.sun_created_at])\
                .where(CommentVersion.sun_comment_id == cls.sun_comment_id)\
                    .order_by(CommentVersion.sun_created_at.desc()).limit(1).as_scalar()

    def to_dict(self):
        main_dict = {
            'sun_comment_id': self.sun_comment_id,
            'sun_post_id': self.sun_post_id,
            'sun_subreddit_id': self.sun_subreddit_id,
            'sun_account_id': self.sun_account_id,
            'most_recent_sun_version_id': self.versions[-1].sun_version_id,
            'most_recent_sun_detail_id': self.most_recent_detail.sun_detail_id,
            'reddit_comment_id': self.reddit_comment_id,
            'reddit_parent_id': self.reddit_parent_id,
            'reddit_post_id': self.reddit_post_id,
            'reddit_account_id': self.reddit_account_id,
            'reddit_unique_id': self.reddit_unique_id,
            'sun_unique_id': self.sun_unique_id,
            'reddit_subreddit_id': self.reddit_subreddit_id,
            'sun_created_at': self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'created_utc': float(self.created_utc),
            'depth': str(self.depth) or '',
            'permalink': self.permalink,
            'is_submitter': self.is_submitter,
            'created': float(self.created),
            'author': self.author.to_dict() if self.author else None,
            "removed" : any([version.removed for version in self.versions]),
            "edited" : any([version.edited for version in self.versions]),
            "deleted" : any([version.deleted for version in self.versions]),
            "versions" : [version.detail.to_dict() for version in self.versions],
            "version_count" : len(self.versions),
            'most_recent_version_updated_at': self.most_recent_version_updated_at.strftime('%d-%m-%Y %H:%M:%S'),
            "post" : self.post.to_dict() if self.post else None,
            "subreddit" : self.subreddit.to_dict() if self.subreddit else None,
        }
        most_recent_details_dict = {k: v for k, v in self.most_recent_detail.to_dict().items()}
        return {**main_dict, **most_recent_details_dict}

class CommentVersion(db.Model):

    __tablename__ = 'comment_versions'
    __table_args__ = (
        Index('ix_comments_comment_versions', 'sun_comment_id', 'sun_comment_version_id', 'sun_comment_detail_id'),
        {'schema': 'comments'}
    )

    sun_comment_id = Column(BigInteger, ForeignKey(Comment.sun_comment_id), primary_key=True, nullable=False)
    sun_comment_version_id = Column(BigInteger, primary_key=True, nullable=False)
    sun_comment_detail_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))

    comment = relationship('Comment', back_populates='versions')
    detail = relationship('CommentDetail', uselist=False, back_populates='version')

    @hybrid_property
    def sun_unique_id(self):
        return self.sun_comment_id

    @hybrid_property
    def sun_version_id(self):
        return self.sun_comment_version_id

    @hybrid_property
    def sun_detail_id(self):
        return self.sun_comment_detail_id


    # TODO:
    # I HAVE DECIDED THAT VERSION AND DETAIL TABLES SHOULD BE MERGED
    # So that the detail has the version id
    # This will make it easier to move variables like removed, edited, deleted to the main table
    # As a workaround, the below works


    # This works here but the init_on_load function conflicts with author on main table posts/comments for some reason
    # This essentially makes the version usable as a detail

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()

    @reconstructor
    def init_on_load(self):
        if self.detail:
            detail_vars = self.detail.to_dict()
            for var, value in detail_vars.items():
                if not hasattr(self, var):
                    setattr(self, var, value)



class CommentDetail(db.Model):
    __tablename__ = 'comment_details'
    __table_args__ = {'schema': 'comments'}

    sun_comment_detail_id = Column(ForeignKey(CommentVersion.sun_comment_detail_id), primary_key=True, index=True)
    sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
    controversiality = Column(BigInteger)
    ups = Column(BigInteger)
    downs = Column(BigInteger)
    score = Column(BigInteger)
    body = Column(Text)
    edited = Column(BigInteger)
    removed = Column(Boolean, nullable=False, default=col_equals('body', '[removed]'))
    deleted = Column(Boolean, nullable=False, default=col_equals('body', '[deleted]'))
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
    source_is_pushshift = Column(Boolean, nullable=False, server_default=text('false'))

    # awardings = relationship('CommentAwarding', back_populates='detail')
    # gildings = relationship('CommentGilding', back_populates='detail')

    version = relationship('CommentVersion', back_populates='detail')

    @hybrid_property
    def sun_detail_id(self):
        return self.sun_comment_detail_id

    def to_dict(self):
        return {
            'sun_comment_detail_id': self.sun_comment_detail_id,
            "sun_comment_version_id" : self.version.sun_comment_version_id,
            "sun_detail_id" : self.sun_comment_detail_id,
            "sun_version_id" : self.version.sun_comment_version_id,
            "sun_unique_id" : self.version.comment.sun_comment_id,
            'sun_created_at': self.sun_created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'controversiality': str(self.controversiality) or '',
            'ups': self.ups,
            'downs': self.downs,
            'score': self.score,
            'body': self.body,
            'edited': self.edited,
            'deleted': self.deleted,
            'removed': self.removed,
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
#     __table_args__ = {'schema': 'public'}

#     sun_awarding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_comment_detail_id = Column(ForeignKey('comment_details.sun_comment_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
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
#     __table_args__ = {'schema': 'public'}

#     sun_gilding_id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, index=True)
#     sun_comment_detail_id = Column(ForeignKey('comment_details.sun_comment_detail_id'), nullable=False)
#     sun_created_at = Column(DateTime, nullable=False, server_default=text("timezone('utc', now())"))
#     reddit_gid = Column(Text)
#     value = Column(Numeric)

#     detail = relationship('CommentDetail', back_populates='gildings')


# # Tables for crawler
# def CrawlerSubredditStatus(db.model):
#     __tablename__ = 'subreddits'
#     __table_args__ = {'schema': 'crawler_status'}

#     sun_subreddit_id = Column(BigInteger, ForeignKey(Subreddit.sun_subreddit_id), primary_key=True, index=True)
#     last_crawled_