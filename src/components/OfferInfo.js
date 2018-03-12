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
      occurencesAtVenue,
      price,
      sellersFavorites,
      thing,
      thingOrEventOccurence,
      thumbUrl,
      venue,
    } = this.props
    return (
      <div>
        <h2> { name } </h2>
        <img alt='' className='offerPicture' src={thumbUrl} />
        <div className='offer-price'>{ price }&nbsp;€</div>
        { description }
        { thing && [ thing.description, <VenueInfo {...venue} /> ] }
        { eventOccurence && [ eventOccurence.event.description, <VenueInfo {...eventOccurence.venue} /> ] }
        { eventOccurence &&
           <ul className='dates'>
             {
               occurencesAtVenue.map((occurence) =>
                                         (
                                           <li>
                                             <span> { occurence.beginningDatetime } </span>
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
