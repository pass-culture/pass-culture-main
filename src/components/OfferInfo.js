import React, { Component } from 'react'
import { connect } from 'react-redux'

import selectMediation from '../selectors/mediation'
import selectOffer from '../selectors/offer'
import selectSource from '../selectors/source'
import selectThumbUrl from '../selectors/thumbUrl'
import selectVenue from '../selectors/venue'

class OfferInfo extends Component {

  render() {
    const { mediation,
      offer,
      source,
      thumbUrl,
      venue,
    } = this.props;

    return (
      <div className='offer-info'>
        {false && <img alt='' className='offerPicture' src={thumbUrl} />}
        {source && source.description && (
          <div className='description'>
            {
              source.description.split('\n')
                                .map((p, index) =>
                <p key={index}>{p}</p>)
            }
          </div>
        )}
        {offer && offer.eventOccurence && (
          <div>
            <h3>Quoi ?</h3>
            <p>{offer.eventOccurence.event.description}</p>
          </div>
        )}
        {offer && offer.occurencesAtVenue && (
          <div>
            <h3>Quand ?</h3>
            <ul className='dates-info'>
              { offer.occurencesAtVenue.map((occurence, index) => (
                <li key={index}>
                  <span> { occurence.beginningDatetime } </span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {venue && venue.address && (
          <div>
            <h3>Où ?</h3>
            <ul className='address-info'>
              <li>{venue.name}</li>
              {venue.address.split(/[,\n\r]/).map((el, index) => (<li key={index}>{el}</li>))}
            </ul>
          </div>
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    mediation: selectMediation(state),
    offer: selectOffer(state),
    source: selectSource(state),
    thumbUrl: selectThumbUrl(state),
    venue: selectVenue(state)
  }))(OfferInfo)
