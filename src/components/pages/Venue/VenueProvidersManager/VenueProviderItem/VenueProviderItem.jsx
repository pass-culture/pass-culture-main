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
      <li className={classnames('is-disabled')}>
        <div className="picto">
          <Icon svg="picto-db-default"/>
        </div>
        <div className="has-text-weight-bold is-size-3">
          {providerName}
        </div>
        <div>
          Compte : {' '}
          <strong className="has-text-weight-bold">
            {venueIdAtOfferProvider}
          </strong>
        </div>
        {lastSyncDate ? (
          [
            numberOfOffers ? (
              <NavLink
                key={0}
                to={`/offres?lieu=${venueId}`}
                className="has-text-primary">
                <Icon svg="ico-offres-r"/>
                {pluralize(numberOfOffers, 'offres')}
              </NavLink>
            ) : (
              <div key={0}>0 offre</div>
            ),
            <div key={1}>
              <button
                className="button is-secondary"
                onClick={this.onDeactivateClick}>
                {isActive ? 'Désactiver' : 'Activer'}
              </button>
            </div>,
          ]
        ) : (
          <div className="small">En cours de validation</div>
        )}
        <div className="is-pulled-right" key={2}>
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
