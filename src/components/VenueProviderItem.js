import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

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
      </div>
    )
  }
}

export default connect(
  null,
  { requestData }
)(VenueProviderItem)
