import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import createOccasionsSelector from '../selectors/createOccasions'
import createVenuesSelector from '../selectors/createVenues'


const OffererItem = ({
  occasions,
  venues,
  offerer
}) => {
  const {
    id,
    name,
    isActive,
  } = (offerer || {})

  const showPath = `/structures/${id}`
  return (
    <li className="offerer-item">
      <div className='list-content'>
        <p className="name">
          <NavLink to={showPath}>
            {name}
          </NavLink>
        </p>
        <ul className='actions'>
          {
            get(venues, 'length') && (
              <li>
                <NavLink to={`/structures/${get(offerer, 'id')}/offres/nouveau`}
                  className='has-text-primary'>
                  <Icon svg='ico-offres-r' /> Créer une offre
                </NavLink>
              </li>
            )
          }
          <li>
            {
              get(occasions, 'length')
                ? (
                  <NavLink to={`/offres?offererId=${id}`} className='has-text-primary'>
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
            {
              get(venues, 'length')
                ? (
                  <NavLink to={showPath}>
                    <Icon svg='picto-structure' />
                    {venues.length} lieux
                  </NavLink>
                )
                : (
                  <p>
                    0 lieu
                  </p>
                )
            }
          </li>
          <li className='is-italic'>{isActive ? 'Activée' : 'En attente de validation'}</li>
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
    return (state, ownProps) => ({
      occasions: createOccasionsSelector()(state, ownProps.offerer.id),
      venues: createVenuesSelector()(state, ownProps.offerer.id),
    })
  }
) (OffererItem)
