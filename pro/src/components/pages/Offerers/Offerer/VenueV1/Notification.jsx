import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { Link } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'

const NotificationMessage = ({ venueId, offererId }) => {
  const notification = useNotification()
  const closeNotification = useCallback(
    () => notification.close(),
    [notification]
  )

  const createOfferPathname = `/offre/creation?lieu=${venueId}&structure=${offererId}`
  return (
    <p>
      Lieu créé. Vous pouvez maintenant y&nbsp;
      <Link onClick={closeNotification} to={createOfferPathname}>
        créer une offre
      </Link>
      , ou en importer automatiquement.
    </p>
  )
}

NotificationMessage.propTypes = {
  offererId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default NotificationMessage
