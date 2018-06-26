import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import createOccasionsSelector from '../selectors/createOccasions'
import createOffersSelector from '../selectors/createOffers'
import createVenuesSelector from '../selectors/createVenues'


const VenueItem = ({
  occasions,
  venue,
}) => {
  const {
    address,
    id,
    managingOffererId,
    name,
  } = (venue || {})

  console.log('occasions', occasions)

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
              get(occasions, 'length')
              ? (
                <NavLink to={`/offres?venueId=${id}`} className='has-text-primary'>
                  <Icon svg='ico-offres-r' />
                   {occasions.length} offres
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

const venuesSelector = createVenuesSelector()
const occasionsSelector = createOccasionsSelector(venuesSelector)
const offersSelector = createOffersSelector()

export default connect(
  () => {
    return (state, ownProps) => {
      const venueId = ownProps.venue.id
      return {
        occasions: occasionsSelector(state, null, venueId),
        offers: offersSelector(state, venueId)
      }
    }
  }
)(VenueItem)
