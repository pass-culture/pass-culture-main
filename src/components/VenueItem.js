import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import createSelectOffers from '../selectors/offers'
import Icon from './layout/Icon'

const VenueItem = ({
  address,
  id,
  managingOffererId,
  name,
  offers
}) => {
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
            {
              get(offers, 'length')
              ? (
                <NavLink to={`/offres?venueId=${id}`} className='has-text-primary'>
                  <Icon svg='ico-offres-r' /> {offers ? offers.length : 0} offres
                </NavLink>
              )
              : (
                <NavLink to={`/structures/${managingOffererId}/lieux/${id}/offres/nouveau`} className='has-text-primary'>
                  <Icon svg='ico-offres-r' /> Créer une offre
                </NavLink>
              )
            }
          </li>
          <li>
            <NavLink to={`/structures/${managingOffererId}/lieux/${id}/fournisseurs/nouveau`}
              className='has-text-primary'>
              <Icon svg='ico-offres-r' /> Importer des offres
            </NavLink>
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
    const selectOffers = createSelectOffers()
    return (state, ownProps) => ({ offers: selectOffers(state, ownProps) })
  }
)(VenueItem)
