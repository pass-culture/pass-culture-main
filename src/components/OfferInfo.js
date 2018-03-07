import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import ControlBar from './ControlBar'
import Icon from './Icon'
import VenueInfo from './VenueInfo'
import withFrontendOffer from '../hocs/withFrontendOffer'
import withSelectors from '../hocs/withSelectors'
import { requestData } from '../reducers/data'

class OfferInfo extends Component {
  render = () => {
    const { 
      description,
      eventOccurence,
      id,
      name,
      price,
      sellersFavorites,
      thing,
      thumbUrl,
      venue,
    } = this.props
    return (
      <div>
        <h2> { name } </h2>
        <img alt='' className='offerPicture' src={thumbUrl} />
        <div className='offer-price'>{ price }&nbsp;€</div>
        { description }
        { thing && <VenueInfo {...venue} /> }
        { eventOccurence &&
           <ul className='dates'>
             {
               eventOccurence.event.eventOccurences.map((offerer) =>
                                         (
                                           <li>
                                             <span> { eventOccurence.beginningDateTime } </span>
                                             <VenueInfo {...venue} />
                                           </li>
                                         ))
             }
           </ul>
        }
        <ControlBar offerId={id} />
      </div>
    )
  }
}

export default compose(
  withFrontendOffer,
  connect(null, { requestData })
)(OfferInfo)
