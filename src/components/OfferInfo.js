import React, { Component } from 'react'
import { connect } from 'react-redux'

import selectOffer from '../selectors/offer'
import selectSource from '../selectors/source'
import selectThumbUrl from '../selectors/thumbUrl'
import selectVenue from '../selectors/venue'

class OfferInfo extends Component {

  render() {
    const {
      offer: {
        eventOccurence,
        occurencesAtVenue,
      },
      source: {
        description,
      },
      venue: {
        name,
        address,
      },
      thumbUrl,
    } = this.props;

    return (
      <div className='offer-info'>
        {false && <img alt='' className='offerPicture' src={thumbUrl} />}
        {description && (
          <div className='description'>
            { description.split('\n').map((p, index) => <p key={index}>{p}</p>) }
          </div>
        )}
        {eventOccurence && (
          <div>
            <h3>Quoi ?</h3>
            <p>{eventOccurence.event.description}</p>
          </div>
        )}
        {occurencesAtVenue && (
          <div>
            <h3>Quand ?</h3>
            <ul className='dates-info'>
              { occurencesAtVenue.map((occurence, index) => (
                <li key={index}>
                  <span> { occurence.beginningDatetime } </span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {address && (
          <div>
            <h3>Où ?</h3>
            <ul className='address-info'>
              <li>{name}</li>
              {address.split(/[,\n\r]/).map((el, index) => (<li key={index}>{el}</li>))}
            </ul>
          </div>
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    source: selectSource(state),
    thumbUrl: selectThumbUrl(state),
    offer: selectOffer(state),
    venue: selectVenue(state)
  }))(OfferInfo)
