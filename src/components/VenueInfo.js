import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { navigationLink } from '../utils/geolocation'
import withFrontendVenue from '../hocs/withFrontendVenue'

import Icon from './Icon'

class VenueInfo extends Component {
  render = () => {
    const { 
      address,
      description,
      thumbCount,
      name,
      latitude,
      longitude,
      thumbUrl,
    } = this.props
    return (
      <div class='venue-info'>
        <img alt='' className='venue-picture' src={thumbUrl} />
        <h3>{name}</h3>
        { description }
        <a href={ navigationLink(latitude, longitude) }>{ address.split('\n').map(a => ( <p> { a } </p> )) }</a>
        <div className='clearfix' />
      </div>
    )
  }
}

export default compose(withFrontendVenue)(VenueInfo)
