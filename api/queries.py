# -*- coding: utf-8 -*-


from .models import *
from .model_lookup import lookup_dict, model_aliases
from ariadne import convert_kwargs_to_snake_case
from datetime import datetime
from sqlalchemy import func, text

def convert_date_timestamp(date):
    try:
        return datetime.strptime(date, '%d-%m-%Y %H:%M:%S').timestamp()
    except ValueError:
        return datetime.strptime(date, '%d-%m-%Y').timestamp()
    except:
        raise ValueError("Invalid date format, should be 'dd-mm-yyyy' or 'dd-mm-yyyy hh:mm:ss'")

def selections(info):
    primary_selections = [x for x in info.field_nodes[0].selection_set.selections if x.name.value == info.field_name]
    if primary_selections:
        primary_selections = primary_selections[0]
        fields = [x.name.value for x in primary_selections.selection_set.selections]
        subfields = {x.name.value : [y.name.value for y in x.selection_set.selections] for x in primary_selections.selection_set.selections if x.selection_set}
        return fields, subfields
    else:
        return [], {}
   

def select_fields(info, results):
    def string_fields_to_sqlalchemy(fields, kind):
        models = lookup_dict[kind]
        fields_dict = {
                models['Main'] : [field for field in fields if hasattr(models['Main'], field)],
                models['Detail'] : [field for field in fields if hasattr(models['Detail'], field)]
            }

        all_sqlalchemy_fields = []
        fields_seen = []
        for table, table_fields in fields_dict.items():
            for field in table_fields:
                if field not in fields_seen:
                    fields_seen.append(field)
                    all_sqlalchemy_fields += [getattr(table, field)]
        
        return all_sqlalchemy_fields


    fields, subfields = selections(info)

    # if not fields, return none because its a total count request
    if fields:

        kind = info.field_name if not info.field_name.endswith('s') else info.field_name[:-1]
        if subfields:
            raise Exception('Subfields not supported.')
            for aliased_kind, fields in subfields.items(): 
                subkind = model_aliases.get(aliased_kind) or aliased_kind
                ids = result.with_entities(text(f'sun_{subkind}_id')).subquery()
                SubModel = lookup_dict[subkind]['Main']
                SubDetail = lookup_dict[subkind]['Detail']
                subresult = SubModel.query.filter(SubModel.sun_unique_id.in_(ids))
                subresult = subresult.with_entities(*string_fields_to_sqlalchemy(fields, kind))


        results = results.with_entities(*string_fields_to_sqlalchemy(fields, kind))


        # convert list of sqlalchemy tuples to list of dicts

        result_dict_list = []
        for result in results.all():
            result_dict = {}
            for field in fields:
                result_dict[field] = result[field]
            result_dict_list += [result_dict]

        return result_dict_list


def payload(results, info, additional_data = None, errors = None):
    kind = info.field_name
    return_list = kind.endswith('s')

    if errors:
        return {"success": False, "errors": errors}

    result = select_fields(info, results)
    return_dict = {"success": True}

    if additional_data:
        return_dict.update(additional_data)

    # If no result, its a total count request
    if result:
        result = result if return_list else result[0]
        return_dict.update({kind : result})
    
    return return_dict

@convert_kwargs_to_snake_case
def resolve_get(obj, info, **kwargs):
    kind = info.field_name
    Model = lookup_dict[kind]['Main']

    by_id = kwargs.get('by_id')
    reddit_id = kwargs.get('reddit_id')
    errors = []

    if by_id and reddit_id:
        errors += ["Cannot specify both by_id and reddit_id"]

    if by_id:
        result = Model.query.filter_by(sun_unique_id=by_id)
        if not result.count():
            errors += [f"No {kind}s found with Sun id {by_id}"]
    if reddit_id:
        result = Model.query.filter_by(reddit_post_id=reddit_id)
        if not result.count():
            errors += [f"No {kind}s found with reddit_id {reddit_id}"]

    return payload(result, info, errors = errors)

@convert_kwargs_to_snake_case
def resolve_get_all(obj, info, **kwargs):
    # determine the singular form of the info.field_name
    # only if it is plural

    kind = info.field_name[:-1]

    Model = lookup_dict[kind]['Main']
    Detail = lookup_dict[kind]['Detail']

    posted_before = kwargs.get('posted_before')
    posted_after = kwargs.get('posted_after')
    updated_before = kwargs.get('updated_before')
    updated_after = kwargs.get('updated_after')
    order_by = kwargs.get('order_by')
    reddit_ids = kwargs.get('reddit_ids')
    sun_subreddit_id = kwargs.get('sun_subreddit_id')
    reddit_subreddit_id = kwargs.get('reddit_subreddit_id')
    sun_account_id = kwargs.get('sun_account_id')
    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    # only look at most recent version of posts
    # potentially later on it may be necessary to filter for all post versions

    results = Model.query.join(Detail).filter(Detail.is_most_recent_version)

    if reddit_ids:
        results = results.filter(Model.reddit_post_id.in_(reddit_ids))

    if sun_subreddit_id:
        results = results.filter(Model.sun_subreddit_id == sun_subreddit_id)

    if sun_account_id:
        results = results.filter(Model.sun_account_id == sun_account_id)

    if updated_before:
        updated_before = int(updated_before)
        results = results.filter(Detail.sun_created_at_epoch < updated_before)
    
    if reddit_subreddit_id:
        results = results.filter(Model.reddit_subreddit_id == reddit_subreddit_id)

    if updated_after:
        updated_after = int(updated_after)
        results = results.filter(Detail.sun_created_at_epoch > updated_after)

    if posted_before:
        posted_before = int(posted_before)
        results = results.filter(Model.sun_created_at_epoch < posted_before)

    if posted_after:
        posted_after = int(posted_after)
        results = results.filter(Model.sun_created_at_epoch > posted_after)


    if order_by: # Not sure this is necessary anymore
        order_by_to_cols = {
            'sun_unique_id' : Model.sun_unique_id,
            'most_recent_sun_version_id': Detail.sun_version_id,
            'most_recent_sun_detail_id': Detail.sun_detail_id
        }

        for col, sort_by in order_by.items():
            col_to_order_by = order_by_to_cols.get(col)
            if sort_by == 'asc':
                results = results.order_by(col_to_order_by.asc())
            elif sort_by == 'desc':
                results = results.order_by(col_to_order_by.desc())

    additional_data = None

    if offset == 0:
        additional_data = {'total_count': results.count()}

    if offset:
        results = results.offset(offset)

    if limit:
        results = results.limit(limit)

    return payload(results, info, additional_data = additional_data)



