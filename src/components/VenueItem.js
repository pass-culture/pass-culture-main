import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import createOffersSelector from '../selectors/createOffers'
import createVenuesSelector from '../selectors/createVenues'


const VenueItem = ({
  venue,
}) => {
  const {
    address,
    id,
    managingOffererId,
    name,
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
            <NavLink to={`/offres/nouveau?lieu=${id}`} className='has-text-primary'>
              <Icon svg='ico-offres-r' /> Créer une offre
            </NavLink>
          </li>
          <li>
            {
              venue.nOccasions && venue.nOccasions > 0
              ? (
                <NavLink to={`/offres?lieu=${id}`} className='has-text-primary'>
                  <Icon svg='ico-offres-r' />
                   {venue.nOccasions} offres
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
const offersSelector = createOffersSelector()

export default connect(
  () => {
    return (state, ownProps) => {
      const venueId = ownProps.venue.id
      return {
        offers: offersSelector(state, venueId)
      }
    }
  }
)(VenueItem)
