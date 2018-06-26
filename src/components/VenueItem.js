import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import createVenueSelector from '../selectors/createVenue'
import createOccasionsSelector from '../selectors/createOccasions'
import createOffersSelector from '../selectors/createOffers'
import Icon from './layout/Icon'

const VenueItem = ({
  offers,
  venue,
}) => {
  const {
    address,
    id,
    managingOffererId,
    name,
    occasions,
  } = (venue || {})
  const showPath = `/structures/${managingOffererId}/lieux/${id}`
  return (
    <li className="venue-item">
      <div className='picto'>
        <Icon svg='picto-structure' />
      </div>
      <div className="list-content">
        <p className="name">
          <NavLink to={showPath}>{name}</NavLink>
        </p>
        <ul className='actions'>
          <li>
            <NavLink to={`/offres/nouveau?offererId=${managingOffererId}&venueId=${id}`} className='has-text-primary'>
              <Icon svg='ico-offres-r' /> Créer une offre
            </NavLink>
          </li>
          <li>
            {
              get(offers, 'length')
              ? (
                <NavLink to={`/offres?venueId=${id}`} className='has-text-primary'>
                  <Icon svg='ico-offres-r' />
                   {offers.length} offres
                </NavLink>
              )
              : (
                <p>
                  Pas encore d'offre
                </p>
              )
            }
          </li>
          <li>
            <p className="has-text-grey">{address}</p>
          </li>
        </ul>
      </div>
      <div className='caret'>
        <NavLink to={showPath}>
          <Icon svg='ico-next-S' />
        </NavLink>
      </div>
    </li>
  )
}

const occasionsSelector = createOccasionsSelector()
const offersSelector = createOffersSelector()
const venueSelector = createVenueSelector()

export default connect(
  () => {
    return (state, ownProps) => ({
      occasions: occasionsSelector(state, null, ownProps.venueId),
      offers: offersSelector(state, {venueId: ownProps.venueId}),
      venue: venueSelector(state, ownProps.venueId)
    })
  }
)(VenueItem)
