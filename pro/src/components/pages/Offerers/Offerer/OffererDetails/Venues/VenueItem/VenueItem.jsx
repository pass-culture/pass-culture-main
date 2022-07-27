import PropTypes from 'prop-types'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

const buildLinkIdFromVenue = ({ publicName, name }) => {
  const nameToFormat = publicName || name
  return nameToFormat ? nameToFormat.toLowerCase().replace(/\s/g, '-') : ''
}

const VenueItem = ({ venue }) => {
  const { address, city, id, managingOffererId, name, postalCode, publicName } =
    venue || {}
  const logEvent = useSelector(state => state.app.logEvent)
  const showPath = `/structures/${managingOffererId}/lieux/${id}`

  return (
    <li className="venue-item">
      <div className="picto">
        <Icon svg="ico-venue" />
      </div>
      <div className="list-content">
        <p className="name">
          <Link id={`a-${buildLinkIdFromVenue(venue)}`} to={showPath}>
            {publicName || name}
          </Link>
        </p>
        <ul className="actions">
          <li>
            <Link
              className="has-text-primary"
              onClick={() =>
                logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                  from: OFFER_FORM_NAVIGATION_IN.OFFERER,
                  to: OFFER_FORM_HOMEPAGE,
                  used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERER_LINK,
                  isEdition: false,
                })
              }
              to={`/offre/creation?lieu=${id}&structure=${managingOffererId}`}
            >
              <AddOfferSvg />
              {' Créer une offre'}
            </Link>
          </li>
          <li>
            <Dotdotdot clamp={2} className="has-text-grey">
              {`${address} ${postalCode} ${city}`}
            </Dotdotdot>
          </li>
        </ul>
      </div>
      <div className="caret">
        <Link to={showPath}>
          <Icon svg="ico-next-S" />
        </Link>
      </div>
    </li>
  )
}

VenueItem.defaultProps = {
  venue: {},
}

VenueItem.propTypes = {
  venue: PropTypes.shape(),
}

export default VenueItem
