from sunbelt.models import *
from ariadne import convert_kwargs_to_snake_case


# create comment
@convert_kwargs_to_snake_case
def resolve_create_comment(obj, info, **praw_obj):
    breakpoint()
    comment_columns = Comment.__table__.c.keys()
    detail_columns = CommentDetail.__table__.c.keys()

    #exists
    comment = Comment.query.filter_by(reddit_comment_id=praw_obj["reddit_comment_id"]).all()

    if len(comments) > 1:
        raise Exception("Multiple comments with same reddit_comment_id: {}".format(praw_obj["reddit_comment_id"]))
    
    last_detail_id = CommentDetail.query.order_by(CommentDetail.zen_comment_detail_id.desc()).first().zen_comment_detail_id
    praw_obj['zen_comment_detail_id'] = last_detail_id + 1

    if len(comments) == 1:  
        comment = comments[0]
        latest_version = CommentVersion.query.filter_by(zen_comment_id=comment.zen_comment_id)\
                                        .order_by(CommentVersion.zen_comment_version_id.desc())\
                                            .first().zen_comment_version_id
        praw_obj['zen_comment_id'] = comment.zen_comment_id
        praw_obj['zen_comment_version_id'] = latest_version + 1
    else:
        last_id = Comment.query.order_by(Comment.zen_comment_id.desc()).first().zen_comment_id
        praw_obj['zen_comment_id'] = last_id + 1
        praw_obj['zen_comment_version_id'] = 1


    comment = {key: praw_obj[key] for key in comment_columns if key in praw_obj}
    details = {key: praw_obj[key] for key in detail_columns if key in praw_obj}
    try:
        due_date = datetime.strptime(due_date, '%d-%m-%Y').date()
        comment = Comment(**kwargs)
        db.session.add(comment)
        db.session.commit()
        payload = {
            "success": True,
            "comment": comment.to_dict()
        }
    except ValueError:  # date format errors
        payload = {
            "success": False,
            "errors": ["Error creating comment"]
        }

    return payload