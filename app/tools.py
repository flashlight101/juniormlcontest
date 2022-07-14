import scipy.sparse as sp
import numpy as np

def get_coo_matrix(df, 
                   user_col='userId', 
                   item_col='movieId', 
                   weight_col=None, 
                   users_mapping={}, 
                   items_mapping={}):
    
    if weight_col is None:
        weights = np.ones(len(df), dtype=np.float32)
    else:
        weights = df[weight_col].astype(np.float32)

    interaction_matrix = sp.coo_matrix((
        weights, 
        (
            df[user_col].map(users_mapping.get), 
            df[item_col].map(items_mapping.get)
        )
    ))
    return interaction_matrix

def generate_implicit_recs_mapper(
    model,
    train_matrix,
    top_N,
    user_mapping,
    item_inv_mapping,
    filter_already_liked_items
):
    def _recs_mapper(user):
        userId = user_mapping[user]
        recs = model.recommend(userId, 
                               train_matrix, 
                               N=top_N, 
                               filter_already_liked_items=filter_already_liked_items)
        return [item_inv_mapping[item] for item, _ in recs]
    return _recs_mapper