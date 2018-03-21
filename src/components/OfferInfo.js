import React from 'react'

import Icon from './Icon'
import withFrontendOffer from '../hocs/withFrontendOffer'
import withSelectors from '../hocs/withSelectors'
import { rgb_to_hsv } from 'colorsys'

const OfferInfo = ({ description,
  eventOccurence,
  id,
  occurencesAtVenue,
  price,
  sellersFavorites,
  thing,
  thingOrEventOccurence,
  thumbUrl,
  venue,
  children,
}) => {
  let style;
  if (thing.firstThumbDominantColor) {
    const [red, green, blue] = thing.firstThumbDominantColor;
    const {h, s, v} = rgb_to_hsv(red, green, blue);
    style = {backgroundColor: `hsl(${h}, 100%, 15%)`};
  }
  return (
    <div className='offer-info'>
      <div className='verso-header' style={style}>
        <h2> { thing.name }, de { thing.extraData.author } </h2>
        <h6> {venue.name} </h6>
      </div>
      {children}
      <div className='content'>
        <img alt='' className='offerPicture' src={thumbUrl} />
        {thing.description && (
          <div className='description'>
            { thing.description.split('\n').map(p => <p key={p}>{p}</p>) }
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
              {venue.address.split(/[,\n\r]/).map(el => (<li key={el}>{el}</li>))}
            </ul>
          </div>
        )}
        <p>
        </p>
      </div>
    </div>
  )
}

export default OfferInfo
