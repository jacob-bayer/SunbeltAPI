DROP SCHEMA IF EXISTS posts CASCADE;
CREATE SCHEMA posts;

/*
 * NOTE: Right now everything links to the detail id, and some columns that I wasn't sure
 * about are in the details table, which is supposed to represent every attribute of a post
 * that can change over time.
 * 
 * If any of those detail columns look like they never change, they can be moved back to the posts table.
 * 
 * If any tables look like they don't have any changing data for each detail (for example, media most likely)
 * then they should be reassigned to link to reference posts.posts(zen_post_id) instead of
 * posts.post_details(zen_detail_id)
 */

-- DROP TABLE posts.posts;
CREATE TABLE posts.posts (
	zen_post_id int8 PRIMARY KEY NOT NULL,
	zen_account_id int8 NULL REFERENCES accounts.accounts(zen_account_id),
	zen_subreddit_id int8 NOT NULL REFERENCES subreddits.subreddits(zen_subreddit_id),
	reddit_post_id text NOT NULL,
	reddit_account_id TEXT NULL,
	reddit_subreddit_id text NOT NULL,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	subreddit_name_prefixed text NOT NULL,
	title text NOT NULL,
	approved_at_utc text NULL,
	subreddit_type text NULL,
	permalink text NULL,
	url text NOT NULL,
	thumbnail_height int8 NULL,
	author_cakeday text null,
	thumbnail_width int8 NULL,
	author_flair_template_id text NULL,
	is_reddit_media_domain bool NULL,
	is_created_from_ads_ui bool NULL,
	post_hint text NULL,
	created float8 NULL,
	domain text NULL,
	no_follow bool NULL,
	created_utc float8 NULL,
	is_video bool NULL
);
CREATE INDEX ix_posts_posts_zen_post_id ON posts.posts USING btree (zen_post_id);



-- DROP TABLE posts.post_versions;
CREATE TABLE posts.post_versions (
	zen_post_id int8 NOT NULL REFERENCES posts.posts(zen_post_id),
	zen_post_version_id int8 NOT NULL,
	zen_post_detail_id int8 NOT NULL UNIQUE,
	zen_created_at timestamp NOT NULL DEFAULT now(),
PRIMARY KEY (zen_post_id, zen_post_version_id, zen_post_detail_id)
);
CREATE INDEX ix_posts_post_versions ON posts.post_versions USING btree (zen_post_id, zen_post_version_id, zen_post_detail_id);


-- DROP TABLE posts.post_details;
CREATE TABLE posts.post_details (
	zen_post_detail_id int8 NOT NULL PRIMARY KEY REFERENCES posts.post_versions(zen_post_detail_id),
	zen_modified_at timestamp NULL,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	gilded bool NULL,
	selftext text NULL,
	downs int8 NULL,
	ups int8 NULL,
	upvote_ratio float8 NULL,
	num_comments int8 NULL,
	num_reports text NULL,
	author_subscribed bool NULL,
	author_is_mod bool NULL,
	comment_limit int8 NULL,
	comment_sort text NULL,
	parent_whitelist_status text NULL,
	stickied bool NULL,
	subreddit_subscribers int8 NULL,
	num_crossposts int8 NULL,
	total_awards_received int8 NULL,
	score int8 NULL,
	author_premium bool NULL,
	edited bool NULL,
	saved bool NULL,
	mod_reason_title text NULL,
	clicked bool NULL,
	hidden bool NULL,
	pwls int8 NULL,
	link_flair_css_class text NULL,
	top_awarded_type text NULL,
	hide_score bool NULL,
	quarantine bool NULL,
	link_flair_text_color text NULL,
	author_flair_background_color text NULL,
	is_original_content bool NULL,
	is_meta bool NULL,
	category text NULL,
	link_flair_text text NULL,
	can_mod_post bool NULL,
	approved_by text NULL,
	thumbnail text NULL,
	author_flair_css_class text NULL,
	is_self bool NULL,
	mod_note text NULL,
	link_flair_type text NULL,
	num_duplicates int4 NULL,
	wls int8 NULL,
	removed_by_category text NULL,
	banned_by text NULL,
	author_flair_type text NULL,
	allow_live_comments bool NULL,
	selftext_html text NULL,
	likes text NULL,
	suggested_sort text NULL,
	banned_at_utc text NULL,
	url_overridden_by_dest text NULL,
	view_count text NULL,
	archived bool NULL,
	is_crosspostable bool NULL,
	pinned bool NULL,
	over_18 bool NULL,
	media_only bool NULL,
	can_gild bool NULL,
	spoiler bool NULL,
	locked bool NULL,
	author_flair_text text NULL,
	visited bool NULL,
	removed_by text NULL,
	distinguished text NULL,
	mod_reason_by text NULL,
	removal_reason text NULL,
	link_flair_background_color text NULL,
	is_robot_indexable bool NULL,
	report_reasons text NULL,
	discussion_type text NULL,
	send_replies bool NULL,
	whitelist_status text NULL,
	contest_mode bool NULL,
	author_patreon_flair bool NULL,
	author_flair_text_color text NULL,
	link_flair_template_id text NULL
);
CREATE INDEX ix_posts_post_details ON posts.post_details USING btree (zen_post_detail_id);



-- DROP TABLE posts.all_awardings;
CREATE TABLE posts.all_awardings (
	zen_awarding_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	zen_post_detail_id int8 NOT NULL REFERENCES posts.post_details(zen_post_detail_id),
	reddit_subreddit_id text NULL,
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
	zen_modified_at timestamp NULL,
	zen_created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_all_awardings_zen_awarding_id ON posts.all_awardings USING btree (zen_awarding_id);



-- DROP TABLE posts.gildings;
CREATE TABLE posts.gildings (
	zen_gilding_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	zen_post_detail_id int8 NOT NULL REFERENCES posts.post_details(zen_post_detail_id),
	reddit_gid text NULL,
	value int8 NULL,
	zen_modified_at timestamp NULL,
	zen_created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_gildings_zen_gilding_id ON posts.gildings USING btree (zen_gilding_id);


-- DROP TABLE posts.media;
CREATE TABLE posts.media (
	zen_media_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	zen_post_detail_id int8 NOT NULL REFERENCES posts.post_details(zen_post_detail_id),
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
	reddit_video_bitrate_kbps float8 null,
	reddit_video_height float8 NULL,
	reddit_video_width float8 NULL,
	reddit_video_scrubber_media_url text NULL,
	reddit_video_dash_url text NULL,
	reddit_video_duration float8 NULL,
	reddit_video_hls_url text NULL,
	reddit_video_is_gif bool NULL,
	reddit_video_transcoding_status text NULL,
	zen_modified_at timestamp NULL,
	zen_created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_media_media_id ON posts.media USING btree (zen_media_id);


-- DROP TABLE posts.media_embed;
CREATE TABLE posts.media_embed (
	zen_media_embed_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	zen_post_detail_id int8 NOT NULL REFERENCES posts.post_details(zen_post_detail_id),
	"content" text NULL,
	width float8 NULL,
	scrolling bool NULL,
	height float8 NULL,
	zen_modified_at timestamp NULL,
	zen_created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_media_embed_zen_media_embed_id ON posts.media_embed USING btree (zen_media_embed_id);


-- DROP TABLE posts.secure_media;
CREATE TABLE posts.secure_media (
	zen_secure_media_id int8 PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	zen_post_detail_id int8 NOT NULL REFERENCES posts.post_details(zen_post_detail_id),
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
	reddit_video_bitrate_kbps float8 null,
	reddit_video_fallback_url text NULL,
	reddit_video_height float8 NULL,
	reddit_video_width float8 NULL,
	reddit_video_scrubber_media_url text NULL,
	reddit_video_dash_url text NULL,
	reddit_video_duration float8 NULL,
	reddit_video_hls_url text NULL,
	reddit_video_is_gif bool NULL,
	reddit_video_transcoding_status text NULL,
	zen_modified_at timestamp NULL,
	zen_created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_posts_secure_media_zen_secure_media_id ON posts.secure_media USING btree (zen_secure_media_id);


/* 
 * This view assumes that the max detail id and max version id will
 * always be associated with one another. There should never be a case
 * where the max detail id is not the max version id. If that happens,
 * this needs to change.
 */
CREATE VIEW posts.most_recent_post_details AS (
SELECT 
reddit_post_id AS reddit_lookup_id,
zen_post_id, 
MAX(zen_post_version_id) AS zen_post_version_id,
MAX(zen_post_detail_id) AS zen_post_detail_id
FROM posts.post_versions
JOIN posts.posts USING (zen_post_id)
GROUP BY zen_post_id, reddit_post_id
)









