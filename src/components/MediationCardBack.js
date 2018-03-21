import React, { Component } from 'react'
// import { connect } from 'react-redux'
// import { compose } from 'redux'
// import { navigationLink } from '../utils/geolocation'

// import Icon from './Icon'

class MediationCardBack extends Component {
  render = () => {
    const {
      backText
    } = this.props
    return (
      <div>
        { backText }
      </div>
    )
  }
}

export default MediationCardBack
