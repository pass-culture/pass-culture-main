/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { CREATION } from 'components/hocs/withFrenchQueryRouter'
import { closeNotification } from 'store/reducers/notificationReducer'

const handleOnClick = dispatch => () => dispatch(closeNotification())
const NotificationMessage = ({ venueId, offererId, dispatch }) => {
  const createOfferPathname = `/offre/${CREATION}?lieu=${venueId}&structure=${offererId}`
  return (
    <p>
      {'Lieu créé. Vous pouvez maintenant y '}
      <Link onClick={handleOnClick(dispatch)} to={createOfferPathname}>
        créer une offre
      </Link>
      {', ou en importer automatiquement. '}
    </p>
  )
}

NotificationMessage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  offererId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default NotificationMessage
