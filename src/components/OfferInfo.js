import React from 'react'

import VenueInfo from './VenueInfo'

const OfferInfo = ({ description,
  eventOccurence,
  id,
  occurencesAtVenue,
  price,
  sellersFavorites,
  thing,
  thingOrEventOccurence,
  thumbUrl,
  venue
}) => {
  return (
    <div>
      <img alt='' className='offerPicture' src={thumbUrl} />
      <div className='offer-price'>{ price }&nbsp;€</div>
      { description }
      {
        thing && [
          <span key={0}>
            {thing.description}
          </span>,
          <VenueInfo key={1} {...venue} />
        ]
      }
      {
        eventOccurence && [
          <span key={2}>
            {eventOccurence.event.description}
          </span>,
          <VenueInfo key={3} {...eventOccurence.venue} />,
          <ul key={4} className='dates'>
            {
              occurencesAtVenue.map((occurence, index) => (
                <li key={index}>
                  <span> { occurence.beginningDatetime } </span>
                </li>
              ))
            }
          </ul>
        ]
      }
    </div>
  )
}

export default OfferInfo
