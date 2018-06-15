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
      id,
      isActive,
      requestData
    } = this.props
    requestData('PATCH', `providers/${id}`, { body: { isActive: !isActive }})
  }

  onDeleteClick = () => {
    const {
      id,
      provider,
      requestData
    } = this.props
    requestData('DELETE', `venueProviders/${id}`, { key: 'venueProviders' })
  }

  render () {
    const {
      venueProvider
    } = this.props
    const {
      isActive,
      provider,
      venueIdAtOfferProvider
    } = (venueProvider || {})
    return (
      <li>
        <div className='picto'>
          <Icon svg='picto-db-default' />
        </div>
        <div className='has-text-weight-bold is-size-3'>
          {provider && provider.localClass}
        </div>
        <div>
          ?? offres
        </div>
        <div>
          Compte : <strong className='has-text-weight-bold'>[{venueIdAtOfferProvider}]</strong>
        </div>
        <div>
          <button className='button is-secondary'
            onClick={this.onDeactivateClick}>
            {isActive ? 'Désactiver': 'Activer'}
          </button>
        </div>
        <div className="is-pulled-right">
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
