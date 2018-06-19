import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import createSelectVenueItem from '../selectors/venueItem'
import Icon from './layout/Icon'

const VenueItem = ({
  venue,
  venueItem
}) => {
  const {
    address,
    id,
    managingOffererId,
    name,
  } = (venue || {})
  const {
    occasions
  } = (venueItem || {})
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
            <NavLink to={`/structures/${managingOffererId}/lieux/${id}/offres/nouveau`} className='has-text-primary'>
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
                  0 offre
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

export default connect(
  () => {
    const selectVenueItem = createSelectVenueItem()
    return (state, ownProps) => ({
      venueItem: selectVenueItem(state, ownProps)
    })
  }
)(VenueItem)
