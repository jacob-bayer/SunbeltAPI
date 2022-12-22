DROP SCHEMA IF EXISTS accounts CASCADE;

CREATE SCHEMA accounts AUTHORIZATION mainuser;
-- accounts.accounts definition

-- Drop table

-- DROP TABLE accounts.accounts;

CREATE TABLE accounts.accounts (
	zen_account_id int8 NOT NULL PRIMARY KEY,
	reddit_account_id text NULL,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	name text NOT NULL,
	created float8 NULL,
	created_utc float8 NULL,
	has_verified_email bool NULL
);
CREATE INDEX ix_accounts_accounts_zen_account_id ON accounts.accounts USING btree (zen_account_id);


CREATE TABLE accounts.account_versions (
	zen_account_id int8 NOT NULL REFERENCES accounts.accounts(zen_account_id),
	zen_account_version_id int8 NOT NULL,
	zen_account_detail_id int8 NOT NULL UNIQUE,
	zen_created_at timestamp NOT NULL DEFAULT now(),
	PRIMARY KEY (zen_account_id, zen_account_version_id, zen_account_detail_id)
);
CREATE INDEX ix_accounts_account_versions ON accounts.account_versions USING btree (zen_account_id, zen_account_version_id, zen_account_detail_id);

/*
 * Break this up into settings details and activity stats details
 */
CREATE TABLE accounts.account_details (
	zen_account_detail_id int8 NOT NULL PRIMARY KEY REFERENCES accounts.account_versions(zen_account_detail_id),
	zen_created_at timestamp NOT NULL DEFAULT now(),
	comment_karma int8 NULL,
	link_karma int8 NULL,
	total_karma int8 NULL,
	awardee_karma int8 NULL,
	awarder_karma int8 NULL,
	listing_use_sort bool NULL,
	is_employee bool NULL,
	snoovatar_size text NULL,
	verified bool NULL,
	is_gold bool NULL,
	icon_img text NULL,
	hide_from_robots bool NULL,
	pref_show_snoovatar bool NULL,
	snoovatar_img text NULL,
	accept_followers bool NULL
);
CREATE INDEX ix_accounts_account_details ON accounts.account_details USING btree (zen_account_detail_id);


/* 
 * This view assumes that the max detail id and max version id will
 * always be associated with one another. There should never be a case
 * where the max detail id is not the max version id. If that happens,
 * this needs to change.
 */
CREATE VIEW accounts.most_recent_details AS (
SELECT DISTINCT ON (zen_account_id)
reddit_account_id AS reddit_lookup_id,
zen_account_id, 
zen_account_version_id,
details.*
FROM accounts.account_versions
JOIN accounts.accounts USING (zen_account_id)
JOIN accounts.account_details details USING (zen_account_detail_id)
ORDER BY zen_account_id, zen_account_version_id DESC
)

