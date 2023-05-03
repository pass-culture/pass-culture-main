import PropTypes from 'prop-types'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'

import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as PlusCircleIcon } from 'icons/ico-plus-circle.svg'
import { ReactComponent as IcoVenue } from 'icons/ico-venue.svg'
import { ButtonLink } from 'ui-kit'

import styles from './VenueItem.module.scss'

const buildLinkIdFromVenue = ({ publicName, name }) => {
  const nameToFormat = publicName || name
  return nameToFormat ? nameToFormat.toLowerCase().replace(/\s/g, '-') : ''
}

const VenueItem = ({ venue, offererId }) => {
  const { address, city, name, postalCode, publicName, nonHumanizedId } =
    venue || {}

  const { logEvent } = useAnalytics()
  const showPath = `/structures/${offererId}/lieux/${nonHumanizedId}`

  return (
    <li>
      <IcoVenue className={styles['picto']} />
      <div className="list-content">
        <ButtonLink
          id={`a-${buildLinkIdFromVenue(venue)}`}
          className="name"
          link={{
            to: showPath,
            isExternal: false,
          }}
        >
          {publicName || name}
        </ButtonLink>
        <ul>
          <li>
            <Dotdotdot clamp={2} className="has-text-grey">
              {`${address} ${postalCode} ${city}`}
            </Dotdotdot>
          </li>
          <li>
            <ButtonLink
              className={styles['create-offer-button']}
              link={{
                to: `/offre/creation?lieu=${nonHumanizedId}&structure=${offererId}`,
                isExternal: false,
              }}
              onClick={() =>
                logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                  from: OFFER_FORM_NAVIGATION_IN.OFFERER,
                  to: OFFER_FORM_HOMEPAGE,
                  used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERER_LINK,
                  isEdition: false,
                })
              }
              Icon={PlusCircleIcon}
            >
              {' Créer une offre'}
            </ButtonLink>
          </li>
        </ul>
      </div>
    </li>
  )
}

VenueItem.defaultProps = {
  venue: {},
}

VenueItem.propTypes = {
  venue: PropTypes.shape(),
  offererId: PropTypes.number,
}

export default VenueItem
