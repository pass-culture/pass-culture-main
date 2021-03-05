from pcapi.utils.logger import logger


class LoggerBackend:
    def update_user_attributes(self, user_id: int, attribute_values: dict) -> None:
        logger.info(
            "A request to update user attributes would be sent for user with id=%d with new attributes=%s",
            user_id,
            attribute_values,
        )
