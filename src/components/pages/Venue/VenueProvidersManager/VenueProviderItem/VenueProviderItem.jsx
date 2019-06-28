import classnames from 'classnames'
import { Icon, pluralize } from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'
import { providerIcons } from './utils/providerIcons'

class VenueProviderItem extends Component {
  render() {
    const {venueProvider} = this.props
    const {lastSyncDate, nOffers, provider, venueIdAtOfferProvider, venueId} = venueProvider
    const {name: providerName, localClass} = provider
    const providerIcon = providerIcons[localClass]

    return (
      <li className={classnames('is-disabled venue-provider-row')}>
        <Icon svg={providerIcon}/>
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
                <Icon svg="ico-offres-r" width="22px" height="22px"/>
                <div className="number-of-offers-label">
                  {pluralize(nOffers, 'offres')}
                </div>
              </NavLink>
            ) : (<div>0 offre</div>)
          )}
        </div>
      </li>
    )
  }
}

VenueProviderItem.propTypes = {
  venueProvider: PropTypes.object
}

export default VenueProviderItem
