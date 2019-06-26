import classnames from 'classnames'
import { Icon, pluralize } from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'

class VenueProviderItem extends Component {
  render() {
    const {venueProvider} = this.props
    const {lastSyncDate, nOffers, provider, venueIdAtOfferProvider, venueId} = venueProvider
    const {name: providerName} = provider

    return (
      <li className={classnames('is-disabled venue-provider-row')}>
        <div className="picto">
          <Icon svg="picto-db-default"/>
        </div>

        <div className="has-text-weight-bold fs14 provider-name-container">
          {providerName}
        </div>

        <div className="fs14 venue-id-at-offer-provider-container">
          Compte : {' '}
          <strong className="fs14 has-text-weight-bold">
            {venueIdAtOfferProvider}
          </strong>
        </div>

        {lastSyncDate ? (
          <div className="offers-container">
            {nOffers ? (
              <NavLink
                className="has-text-primary"
                to={`/offres?lieu=${venueId}`}
              >
                <Icon svg="ico-offres-r" width="20px" height="20px"/>
                <div className="number-of-offers-label">{pluralize(nOffers, 'offres')}</div>
              </NavLink>
            ) : (
              <div>0 offre</div>
            )}
          </div>
        ) : (
          <div className="fs14 validation-label-container">En cours de validation</div>
        )}
      </li>
    )
  }
}

VenueProviderItem.propTypes = {
  venueProvider: PropTypes.object
}

export default VenueProviderItem
