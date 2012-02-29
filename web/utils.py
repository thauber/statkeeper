def getOrNone(model, **kwargs):
    try:
        obj = model.get(**kwargs)
    except e, model.DoesNotExist:
        obj = None
    return obj
