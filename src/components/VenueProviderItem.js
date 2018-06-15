import classnames from 'classnames'
import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
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
    requestData('PATCH', `providers/${id}`, { body: { isActive: !isActive }})
  }

  onDeleteClick = () => {
    const {
      provider,
      requestData,
      venueProvider
    } = this.props
    const { id } = (venueProvider || {})
    requestData('DELETE', `venueProviders/${id}`, { key: 'venueProviders' })
  }

  render () {
    const {
      venueProvider
    } = this.props
    const {
      isActive,
      lastSyncDate,
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
            <div key={0}>
              ?? offres
            </div>,
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
