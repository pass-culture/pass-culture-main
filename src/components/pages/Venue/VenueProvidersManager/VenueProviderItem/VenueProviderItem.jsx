import classnames from 'classnames'
import get from 'lodash.get'
import { Icon, pluralize } from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'
import PropTypes from 'prop-types'

class VenueProviderItem extends Component {
  onDeactivateClick = () => {
    const {dispatch, venueProvider} = this.props
    const {id, isActive} = venueProvider || {}

    dispatch(
      requestData({
        apiPath: `/venueProviders/${id}`,
        body: {
          isActive: !isActive
        },
        method: 'PATCH',
      })
    )
  }

  onDeleteClick = () => {
    const {dispatch, venueProvider} = this.props
    const {id} = venueProvider || {}

    dispatch(
      requestData({
        apiPath: `/venueProviders/${id}`,
        method: 'DELETE',
        stateKey: 'venueProviders',
      })
    )
  }

  render() {
    const {events, things, venue, venueProvider} = this.props
    const {isActive, lastSyncDate, provider, venueIdAtOfferProvider} = venueProvider || {}
    const numberOfOffers = (events || []).concat(things).length
    const providerName = get(provider, 'name')
    const venueId = get(venue, 'id')

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
          <strong className="has-text-weight-bold fs14">
            {venueIdAtOfferProvider}
          </strong>
        </div>

        {lastSyncDate ? (
          <div>
            <div className="offers-container">
              {numberOfOffers ? (
                <NavLink
                  className="has-text-primary"
                  to={`/offres?lieu=${venueId}`}
                >
                  <Icon svg="ico-offres-r"/>
                  {pluralize(numberOfOffers, 'offres')}
                </NavLink>
              ) : (
                <div>0 offre</div>
              )}
            </div>

            <div className="button-container">
              <button
                className="button is-secondary enable-disable-button"
                onClick={this.onDeactivateClick}>
                {isActive ? 'Désactiver' : 'Activer'}
              </button>
            </div>
          </div>
        ) : (
          <div className="fs14 validation-label-container">En cours de validation</div>
        )}
        <div>
          <button className="delete is-small" onClick={this.onDeleteClick}/>
        </div>
      </li>
    )
  }
}

VenueProviderItem.propTypes = {
  events: PropTypes.array,
  things: PropTypes.array,
  venue: PropTypes.object,
  venueProvider: PropTypes.object
}

export default VenueProviderItem
