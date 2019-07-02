import { Icon, pluralize } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'
import { PROVIDER_ICONS } from './utils/providerIcons'

const VenueProviderItem = ({venueProvider}) => {
  const {lastSyncDate, nOffers, provider, venueIdAtOfferProvider, venueId} = venueProvider
  const {name: providerName, localClass} = provider
  const providerIcon = PROVIDER_ICONS[localClass]

  return (
    <li className="venue-provider-row">
      <Icon svg={providerIcon} />
      <div className="has-text-weight-bold fs14 provider-name-container">
        {providerName}
      </div>

      <div className="fs14 venue-id-at-offer-provider-container">
        <div>
          Compte : {' '}
          <strong className="fs14 has-text-weight-bold">
            {venueIdAtOfferProvider}
          </strong>

          {!lastSyncDate && (
            <div className="fs14 import-label-container">
              Importation en cours. Cette étape peut durer plusieurs dizaines de minutes.
            </div>
          )}
        </div>
      </div>

      <div className="offers-container">
        {lastSyncDate && (
          nOffers ? (
            <NavLink
              className="has-text-primary"
              to={`/offres?lieu=${venueId}`}
            >
              <Icon svg="ico-offres-r" width="22px" height="22px" />
              <div className="number-of-offers-label">
                {pluralize(nOffers, 'offres')}
              </div>
            </NavLink>
          ) : (
            <div className="number-of-offers-label">
              0 offre
            </div>
          )
        )}
      </div>
    </li>
  )
}

VenueProviderItem.propTypes = {
  venueProvider: PropTypes.object
}

export default VenueProviderItem
