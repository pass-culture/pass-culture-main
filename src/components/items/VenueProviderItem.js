import classnames from 'classnames'
import get from 'lodash.get'
import { Icon, pluralize, requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import eventsSelector from '../../selectors/events'
import thingsSelector from '../../selectors/things'

class VenueProviderItem extends Component {
  onDeactivateClick = () => {
    const { isActive, requestData, venueProvider } = this.props
    const { id } = venueProvider || {}
    requestData('PATCH', `venueProviders/${id}`, {
      body: { isActive: !isActive },
    })
  }

  onDeleteClick = () => {
    const { requestData, venueProvider } = this.props
    const { id } = venueProvider || {}
    requestData('DELETE', `venueProviders/${id}`, { key: 'venueProviders' })
  }

  render() {
    const { events, things, venue, venueProvider } = this.props
    const { isActive, lastSyncDate, provider, venueIdAtOfferProvider } =
      venueProvider || {}
    const nOffers = (events || []).concat(things).length

    return (
      <li className={classnames('is-disabled')}>
        <div className="picto">
          <Icon svg="picto-db-default" />
        </div>
        <div className="has-text-weight-bold is-size-3">
          {get(provider, 'localClass')}
        </div>
        <div>
          Compte :{' '}
          <strong className="has-text-weight-bold">
            [{venueIdAtOfferProvider}]
          </strong>
        </div>
        {lastSyncDate ? (
          [
            nOffers ? (
              <NavLink
                key={0}
                to={`/offres?lieu=${get(venue, 'id')}`}
                className="has-text-primary">
                <Icon svg="ico-offres-r" />
                {pluralize(nOffers, 'offres')}
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
          <button className="delete is-small" onClick={this.onDeleteClick} />
        </div>
      </li>
    )
  }
}

export default compose(
  connect(
    (state, ownProps) => ({
      events: eventsSelector(state, ownProps.venueProvider.providerId),
      things: thingsSelector(state, ownProps.venueProvider.providerId),
    }),
    { requestData }
  )
)(VenueProviderItem)
