import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

import { pluralize } from '../../../../../../utils/pluralize'
import { PROVIDER_ICONS } from '../../../../../utils/providers'

const VenueProviderItem = ({ venueProvider }) => {
  const { lastSyncDate, nOffers, provider, venueIdAtOfferProvider } = venueProvider
  const { name: providerName, localClass } = provider
  const providerIcon = PROVIDER_ICONS[localClass]

  return (
    <li className="venue-provider-row">
      <Icon
        height="64px"
        svg={providerIcon}
        width="64px"
      />

      <div className="provider-name-container">
        {providerName}
      </div>

      {!lastSyncDate ? (
        <div className="venue-id-at-offer-provider-container-with-message">
          <div className="venue-id-at-offer-provider">
            {'Compte : '}
            <strong>
              {venueIdAtOfferProvider}
            </strong>
          </div>
          <div className="import-label-container">
            {'Importation en cours.' +
              ' Cette étape peut durer plusieurs dizaines de minutes.' +
              ' Vous pouvez fermer votre navigateur et revenir plus tard.'}
          </div>
        </div>
      ) : (
        <div className="venue-id-at-offer-provider-container">
          <div className="venue-id-at-offer-provider">
            {'Compte : '}
            <strong>
              {venueIdAtOfferProvider}
            </strong>
          </div>
          <div className="offers-container-counter">
            <Icon
              height="22px"
              svg="ico-offres-r"
              width="22px"
            />
            <div className="number-of-offers-label">
              {pluralize(nOffers, 'offres')}
            </div>
          </div>
        </div>
      )}
    </li>
  )
}

VenueProviderItem.propTypes = {
  venueProvider: PropTypes.shape().isRequired,
}

export default VenueProviderItem
