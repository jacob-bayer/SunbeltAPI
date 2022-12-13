DROP SCHEMA IF EXISTS accounts CASCADE;

CREATE SCHEMA accounts AUTHORIZATION mainuser;
-- accounts.accounts definition

-- Drop table

-- DROP TABLE accounts.accounts;

CREATE TABLE accounts.accounts (
	zen_account_id int8 NOT NULL PRIMARY KEY,
	reddit_account_id text NULL,
	zen_modified_at timestamp NOT NULL,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	"name" text NOT NULL,
	comment_karma int8 NULL,
	link_karma int8 NULL,
	total_karma int8 NULL,
	awardee_karma int8 NULL,
	awarder_karma int8 NULL,
	listing_use_sort bool NULL,
	is_employee bool NULL,
	snoovatar_size text NULL,
	created float8 NULL,
	created_utc float8 NULL,
	verified bool NULL,
	is_gold bool NULL,
	has_verified_email bool NULL,
	icon_img text NULL,
	hide_from_robots bool NULL,
	pref_show_snoovatar bool NULL,
	snoovatar_img text NULL,
	accept_followers bool NULL
);
CREATE INDEX ix_accounts_accounts_zen_account_id ON accounts.accounts USING btree (zen_account_id);
