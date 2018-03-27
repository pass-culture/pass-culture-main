import React, { Component } from 'react'
import { connect } from 'react-redux'

import currentSource from '../selectors/currentSource'
import currentVenue from '../selectors/currentVenue'
import currentThumbUrl from '../selectors/currentThumbUrl'
import currentOffer from '../selectors/currentOffer'

class OfferInfo extends Component {

  render() {
    const {
      currentOffer: {
        eventOccurence,
        occurencesAtVenue,
      },
      currentSource: {
        description,
      },
      currentVenue: {
        name,
        address,
      },
      currentThumbUrl,
    } = this.props;

    return (
      <div className='offer-info'>
        {false && <img alt='' className='offerPicture' src={currentThumbUrl} />}
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
    currentSource: currentSource(state),
    currentVenue: currentVenue(state),
    currentThumbUrl: currentThumbUrl(state),
    currentOffer: currentOffer(state),
  }))(OfferInfo)