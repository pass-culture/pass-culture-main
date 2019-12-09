import React from 'react'
import { closeNotification } from 'pass-culture-shared'
import { CREATION } from '../../hocs/withFrenchQueryRouter'
import { NavLink } from 'react-router-dom'

const handleOnClick = dispatch => () => dispatch(closeNotification())
const NotificationMessage = ({ venueId, offererId, dispatch }) => {
  const createOfferPathname = `/offres/${CREATION}?lieu=${venueId}&structure=${offererId}`
  return (
    <p>
      {'Lieu créé. Vous pouvez maintenant y '}
      <NavLink
        onClick={handleOnClick(dispatch)}
        to={createOfferPathname}
      >
        {'créer une offre'}
      </NavLink>
      {', ou en importer automatiquement. '}
    </p>
  )
}

export default NotificationMessage
