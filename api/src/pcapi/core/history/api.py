from pcapi.core.history import models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.repository import repository


def log_action(
    action_type: models.ActionType,
    author: users_models.User | None,
    user: users_models.User | None = None,
    offerer: offerers_models.Offerer | None = None,
    venue: offerers_models.Venue | None = None,
    comment: str | None = None,
    save: bool = True,
    **extra_data: dict,
) -> models.ActionHistory:
    """
    Set save parameter to False if you want to save the returned object at the same time as modified resources.

    Be careful: author/user/offerer/venue object and its id may not be associated before the action is saved and/or
    before the new object itself is inserted in the database. RuntimeError are issued in case this function would save
    new resources in parameters; when such an exception is raised, it shows a bug in our code.
    """
    if not user and not offerer and not venue:
        raise ValueError("No resource (user, offerer, venue)")

    if save:
        if user is not None and user.id is None:
            raise RuntimeError("Unsaved user would be saved with action: %s" % (user.email,))

        if offerer is not None and offerer.id is None:
            raise RuntimeError("Unsaved offerer would be saved with action: %s" % (offerer.name,))

        if venue is not None and venue.id is None:
            raise RuntimeError("Unsaved venue would be saved with action %s" % (venue.name,))

    if not isinstance(author, users_models.User):
        # None or AnonymousUserMixin
        # Examples: offerer validated by token (without authentication), offerer created by script
        author = None

    action = models.ActionHistory(
        actionType=action_type,
        authorUser=author,
        user=user,
        offerer=offerer,
        venue=venue,
        comment=comment,
        extraData=extra_data,
    )

    if save:
        repository.save(action)

    return action
