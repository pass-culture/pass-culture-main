import React, { Component } from 'react'

class OfferInfo extends Component {

  render() {
    const {
      // id,
      // description,
      // price,
      // sellersFavorites,
      // thingOrEventOccurence,
      eventOccurence,
      occurencesAtVenue,
      thing,
      thumbUrl,
      venue,
    } = this.props;

    return (
      <div className='offer-info'>
        <img alt='' className='offerPicture' src={thumbUrl} />
        {thing.description && (
          <div className='description'>
            { thing.description.split('\n').map((p, index) => <p key={index}>{p}</p>) }
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
        {venue.address && (
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

export default OfferInfo
