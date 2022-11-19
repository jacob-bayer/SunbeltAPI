DROP SCHEMA posts CASCADE;
CREATE SCHEMA posts AUTHORIZATION mainuser;



-- DROP TABLE posts.posts;
CREATE TABLE posts.posts (
	post_id int8 PRIMARY KEY NOT NULL,
	id text NULL,
	reddit_post_id text NULL,
	reddit_account_id text NULL,
	reddit_subreddit_id text NULL,
	modified_at timestamp NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	subreddit_name_prefixed text NULL,
	title text NULL,
	gilded int8 NULL,
	selftext text NULL,
	approved_at_utc text NULL,
	downs int8 NULL,
	subreddit_type text NULL,
	ups int8 NULL,
	upvote_ratio float8 NULL,
	permalink text NULL,
	num_reports text NULL,
	comment_limit int8 NULL,
	comment_sort text NULL,
	saved bool NULL,
	mod_reason_title text NULL,
	clicked bool NULL,
	hidden bool NULL,
	pwls int8 NULL,
	link_flair_css_class text NULL,
	thumbnail_height int8 NULL,
	top_awarded_type text NULL,
	hide_score bool NULL,
	quarantine bool NULL,
	link_flair_text_color text NULL,
	author_flair_background_color text NULL,
	author_cakeday text null,
	total_awards_received int8 NULL,
	thumbnail_width int8 NULL,
	author_flair_template_id text NULL,
	is_original_content bool NULL,
	is_reddit_media_domain bool NULL,
	is_meta bool NULL,
	category text NULL,
	link_flair_text text NULL,
	can_mod_post bool NULL,
	score int8 NULL,
	approved_by text NULL,
	is_created_from_ads_ui bool NULL,
	author_premium bool NULL,
	thumbnail text NULL,
	edited bool NULL,
	author_flair_css_class text NULL,
	post_hint text NULL,
	is_self bool NULL,
	mod_note text NULL,
	created float8 NULL,
	link_flair_type text NULL,
	num_duplicates int4 NULL,
	wls int8 NULL,
	removed_by_category text NULL,
	banned_by text NULL,
	author_flair_type text NULL,
	"domain" text NULL,
	allow_live_comments bool NULL,
	selftext_html text NULL,
	likes text NULL,
	suggested_sort text NULL,
	banned_at_utc text NULL,
	url_overridden_by_dest text NULL,
	view_count text NULL,
	archived bool NULL,
	no_follow bool NULL,
	is_crosspostable bool NULL,
	pinned bool NULL,
	over_18 bool NULL,
	media_only bool NULL,
	can_gild bool NULL,
	spoiler bool NULL,
	"locked" bool NULL,
	author_flair_text text NULL,
	visited bool NULL,
	removed_by text NULL,
	distinguished text NULL,
	author_is_blocked bool NULL,
	mod_reason_by text NULL,
	removal_reason text NULL,
	link_flair_background_color text NULL,
	is_robot_indexable bool NULL,
	report_reasons text NULL,
	discussion_type text NULL,
	num_comments int8 NULL,
	send_replies bool NULL,
	whitelist_status text NULL,
	contest_mode bool NULL,
	author_patreon_flair bool NULL,
	author_flair_text_color text NULL,
	parent_whitelist_status text NULL,
	stickied bool NULL,
	url text NULL,
	subreddit_subscribers int8 NULL,
	created_utc float8 NULL,
	num_crossposts int8 NULL,
	is_video bool NULL,
	fetched bool NULL,
	link_flair_template_id text NULL
);
CREATE INDEX ix_posts_posts_post_id ON posts.posts USING btree (post_id);


-- DROP TABLE posts.all_awardings;
CREATE TABLE posts.all_awardings (
	awarding_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	post_id int8 NOT NULL REFERENCES posts.posts(post_id),
	giver_coin_reward text NULL,
	is_new bool NULL,
	days_of_drip_extension float8 NULL,
	coin_price int8 NULL,
	id text NULL,
	penny_donate text NULL,
	coin_reward int8 NULL,
	icon_url text NULL,
	days_of_premium float8 NULL,
	icon_height int8 NULL,
	icon_width int8 NULL,
	static_icon_width int8 NULL,
	start_date float8 NULL,
	is_enabled bool NULL,
	awardings_required_to_grant_benefits float8 NULL,
	description text NULL,
	end_date float8 NULL,
	sticky_duration_seconds text NULL,
	subreddit_coin_reward int8 NULL,
	count int8 NULL,
	static_icon_height int8 NULL,
	"name" text NULL,
	icon_format text NULL,
	award_sub_type text NULL,
	penny_price float8 NULL,
	award_type text NULL,
	static_icon_url text NULL,
	reddit_subreddit_id text NULL,
	modified_at timestamp NULL,
	created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_all_awardings_awarding_id ON posts.all_awardings USING btree (awarding_id);



-- DROP TABLE posts.gildings;
CREATE TABLE posts.gildings (
	gilding_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	post_id int8 NOT NULL REFERENCES posts.posts(post_id),
	reddit_gid text NULL,
	value int8 NULL,
	modified_at timestamp NULL,
	created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_gildings_gilding_id ON posts.gildings USING btree (gilding_id);


-- DROP TABLE posts.media;
CREATE TABLE posts.media (
	media_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	post_id int8 NOT NULL REFERENCES posts.posts(post_id),
	"type" text NULL,
	oembed_provider_url text NULL,
	oembed_version text NULL,
	oembed_title text NULL,
	oembed_type text NULL,
	oembed_thumbnail_width float8 NULL,
	oembed_height float8 NULL,
	oembed_width float8 NULL,
	oembed_html text NULL,
	oembed_author_name text NULL,
	oembed_provider_name text NULL,
	oembed_thumbnail_url text NULL,
	oembed_thumbnail_height float8 NULL,
	oembed_author_url text NULL,
	reddit_video_fallback_url text NULL,
	reddit_video_height float8 NULL,
	reddit_video_width float8 NULL,
	reddit_video_scrubber_media_url text NULL,
	reddit_video_dash_url text NULL,
	reddit_video_duration float8 NULL,
	reddit_video_hls_url text NULL,
	reddit_video_is_gif bool NULL,
	reddit_video_transcoding_status text NULL,
	modified_at timestamp NULL,
	created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_media_media_id ON posts.media USING btree (media_id);


-- DROP TABLE posts.media_embed;
CREATE TABLE posts.media_embed (
	media_embed_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	post_id int8 NOT NULL REFERENCES posts.posts(post_id),
	"content" text NULL,
	width float8 NULL,
	scrolling bool NULL,
	height float8 NULL,
	modified_at timestamp NULL,
	created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_media_embed_media_embed_id ON posts.media_embed USING btree (media_embed_id);


-- DROP TABLE posts.secure_media;
CREATE TABLE posts.secure_media (
	secure_media_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	post_id int8 NOT NULL REFERENCES posts.posts(post_id),
	"type" text NULL,
	oembed_provider_url text NULL,
	oembed_version text NULL,
	oembed_title text NULL,
	oembed_type text NULL,
	oembed_thumbnail_width float8 NULL,
	oembed_height float8 NULL,
	oembed_width float8 NULL,
	oembed_html text NULL,
	oembed_author_name text NULL,
	oembed_provider_name text NULL,
	oembed_thumbnail_url text NULL,
	oembed_thumbnail_height float8 NULL,
	oembed_author_url text NULL,
	reddit_video_fallback_url text NULL,
	reddit_video_height float8 NULL,
	reddit_video_width float8 NULL,
	reddit_video_scrubber_media_url text NULL,
	reddit_video_dash_url text NULL,
	reddit_video_duration float8 NULL,
	reddit_video_hls_url text NULL,
	reddit_video_is_gif bool NULL,
	reddit_video_transcoding_status text NULL,
	modified_at timestamp NULL,
	created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_secure_media_secure_media_id ON posts.secure_media USING btree (secure_media_id);



