import classnames from 'classnames'
import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Icon from './layout/Icon'
import { requestData } from '../reducers/data'

class VenueProviderItem extends Component {

  onDeactivateClick = () => {
    const {
      isActive,
      requestData,
      venueProvider
    } = this.props
    const { id } = (venueProvider || {})
    requestData(
      'PATCH',
      `venueProviders/${id}`,
      {
        body: { isActive: !isActive }
      }
    )
  }

  onDeleteClick = () => {
    const {
      requestData,
      venueProvider
    } = this.props
    const { id } = (venueProvider || {})
    requestData('DELETE', `venueProviders/${id}`, { key: 'venueProviders' })
  }

  render () {
    const {
      currentVenue,
      venueProvider
    } = this.props
    const {
      isActive,
      lastSyncDate,
      occasions,
      provider,
      venueIdAtOfferProvider
    } = (venueProvider || {})

    return (
      <li className={classnames('is-disabled')}>
        <div className='picto'>
          <Icon svg='picto-db-default' />
        </div>
        <div className='has-text-weight-bold is-size-3'>
          {provider && provider.localClass}
        </div>
        <div>
          Compte : <strong className='has-text-weight-bold'>
            [{venueIdAtOfferProvider}]
          </strong>
        </div>
        {
          lastSyncDate
          ? [
            get(occasions, 'length')
              ? (
                <NavLink key={0} to={`/offres?structure=${get(currentVenue, 'id')}`}
                  className='has-text-primary'>
                  <Icon svg='ico-offres-r' />
                  {occasions.length} offres
                </NavLink>
              )
              : (
                <div key={0}>
                  0 offre
                </div>
              ),
            <div key={1}>
              <button className='button is-secondary'
                onClick={this.onDeactivateClick}>
                {isActive ? 'Désactiver': 'Activer'}
              </button>
            </div>
          ]
          : (
            <div className='small'>
              En cours de validation
            </div>
          )
        }
        <div className="is-pulled-right" key={2}>
          <button className="delete is-small"
            onClick={this.onDeleteClick} />
        </div>
      </li>
    )
  }
}

export default compose(
  connect(
    null,
    { requestData }
  )
)(VenueProviderItem)
