import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

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
      identifier,
      isActive,
      provider
    } = this.props
    return (
      <div className="box offerer-provider-item">
        <h2 className="subtitle"> {get(provider, 'name')} </h2>
        <i> {identifier} </i>
        <button onClick={this.onDeactivateClick}>
          {isActive ? 'Désactiver': 'Activer'}
        </button>
        <button onClick={this.onDeleteClick}>
          Enlever
        </button>
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    null,
    { requestData }
  )
)(VenueProviderItem)
