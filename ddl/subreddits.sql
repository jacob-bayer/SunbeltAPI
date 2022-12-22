DROP SCHEMA IF EXISTS subreddits CASCADE;

CREATE SCHEMA subreddits AUTHORIZATION mainuser;
-- subreddits.subreddits definition

-- Drop table

-- DROP TABLE subreddits.subreddits;

CREATE TABLE subreddits.subreddits (
	zen_subreddit_id int8 NOT NULL PRIMARY KEY,
	reddit_subreddit_id text NOT NULL,
	display_name_prefixed text NULL,
	url text NOT NULL,
	title text NULL,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	display_name text NULL,
	created float8 NULL,
	lang text NULL,
	created_utc float8 NULL,
	path text NULL,
	is_enrolled_in_new_modmail text NULL
);
CREATE INDEX ix_subreddits_subreddits_zen_subreddit_id ON subreddits.subreddits USING btree (zen_subreddit_id);


CREATE TABLE subreddits.subreddit_versions (
	zen_subreddit_id int8 NOT NULL REFERENCES subreddits.subreddits(zen_subreddit_id),
	zen_subreddit_version_id int8 NOT NULL,
	zen_subreddit_detail_id int8 NOT NULL UNIQUE,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	PRIMARY KEY (zen_subreddit_id, zen_subreddit_version_id, zen_subreddit_detail_id)
);
CREATE INDEX ix_subreddits_subreddit_versions ON subreddits.subreddit_versions USING btree (zen_subreddit_id, zen_subreddit_version_id, zen_subreddit_detail_id);

/*
 * Break this up into settings details and activity stats details
 */
CREATE TABLE subreddits.subreddit_details (
	zen_subreddit_detail_id int8 NOT NULL PRIMARY KEY REFERENCES subreddits.subreddit_versions(zen_subreddit_detail_id),
	zen_created_at timestamp NOT NULL DEFAULT now(),
	active_user_count int8 NULL,
	accounts_active int8 NULL,
	public_traffic bool NULL,
	subscribers int8 NULL,
	subreddit_type text NULL,
	suggested_comment_sort text NULL,
	allow_polls bool NULL,
	collapse_deleted_comments bool NULL,
	public_description_html text NULL,
	allow_videos bool NULL,
	allow_discovery bool NULL,
	accept_followers bool NULL,
	is_crosspostable_subreddit bool NULL,
	notification_level text NULL,
	should_show_media_in_comments_setting bool NULL,
	user_flair_background_color text NULL,
	submit_text_html text NULL,
	restrict_posting bool NULL,
	free_form_reports bool NULL,
	wiki_enabled bool NULL,
	header_img text NULL,
	allow_galleries bool NULL,
	primary_color text NULL,
	icon_img text NULL,
	quarantine bool NULL,
	hide_ads bool NULL,
	prediction_leaderboard_entry_type text NULL,
	emojis_enabled bool NULL,
	advertiser_category text NULL,
	public_description text NULL,
	comment_score_hide_mins int8 NULL,
	allow_predictions bool NULL,
	community_icon text NULL,
	banner_background_image text NULL,
	original_content_tag_enabled bool NULL,
	community_reviewed bool NULL,
	submit_text text NULL,
	description_html text NULL,
	spoilers_enabled bool NULL,
	allow_talks bool NULL,
	all_original_content bool NULL,
	has_menu_widget bool NULL,
	key_color text NULL,
	wls int8 NULL,
	show_media_preview bool NULL,
	submission_type text NULL,
	allow_videogifs bool NULL,
	should_archive_posts bool NULL,
	can_assign_link_flair bool NULL,
	accounts_active_is_fuzzed bool NULL,
	allow_prediction_contributors bool NULL,
	submit_text_label text NULL,
	link_flair_position text NULL,
	allow_chat_post_creation bool NULL,
	user_sr_theme_enabled bool NULL,
	link_flair_enabled bool NULL,
	disable_contributor_requests bool NULL,
	banner_img text NULL,
	content_category text NULL,
	banner_background_color text NULL,
	show_media bool NULL,
	over18 bool NULL,
	header_title text NULL,
	description text NULL,
	is_chat_post_feature_enabled bool NULL,
	submit_link_label text NULL,
	restrict_commenting bool NULL,
	allow_images bool NULL,
	whitelist_status text NULL,
	mobile_banner_image text NULL,
	allow_predictions_tournament bool NULL,
	videostream_links_count float8 NULL
);
CREATE INDEX ix_subreddits_subreddit_details ON subreddits.subreddit_details USING btree (zen_subreddit_detail_id);


/* 
 * This view assumes that the max detail id and max version id will
 * always be associated with one another. There should never be a case
 * where the max detail id is not the max version id. If that happens,
 * this needs to change.
 */
CREATE VIEW subreddits.most_recent_details AS (
SELECT DISTINCT ON (zen_subreddit_id)
reddit_subreddit_id AS reddit_lookup_id,
zen_subreddit_id, 
zen_subreddit_version_id,
details.*
FROM subreddits.subreddit_versions
JOIN subreddits.subreddits USING (zen_subreddit_id)
JOIN subreddits.subreddit_details details USING (zen_subreddit_detail_id)
ORDER BY zen_subreddit_id, zen_subreddit_version_id DESC
)




