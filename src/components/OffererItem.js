import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import createSelectManagedOccasions from '../selectors/managedOccasions'
import createSelectManagedVenues from '../selectors/managedVenues'


const OffererItem = ({
  managedOccasions,
  managedVenues,
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
          {!isActive ? (
            <li className='is-italic'>En cours de validation : vous allez recevoir un e-mail.</li>
          ) : (
            [
              <li>
                {
                  get(managedVenues, 'length')
                  ? (
                    <NavLink to={`/offres/nouveau`} className='has-text-primary'>
                    <Icon svg='ico-offres-r' />
                    Nouvelle offre
                  </NavLink>
                ) :
                ''
                }
              </li>,
              <li>
                {
                  get(managedOccasions, 'length')
                    ? (
                      <NavLink to={`/offres?offererId=${id}`} className='has-text-primary'>
                        <Icon svg='ico-offres-r' />
                        {managedOccasions.length} offre
                      </NavLink>
                    )
                    : ( get(managedVenues, 'length') ? (
                      <p>
                        0 offre
                      </p>
                    ) : ''
                    )
                }
              </li>,
              <li>
                {
                  get(managedVenues, 'length')
                    ? (
                      <NavLink to={showPath}>
                        <Icon svg='picto-structure' />
                        {managedVenues.length} lieu
                      </NavLink>
                      )
                    : (
                      [
                        <p>Vous devez avoir déjà enregistré un lieu pour ajouter des offres</p>,
                        <NavLink to={`/structures/${get(offerer, 'id')}/lieux/nouveau`}
                        className='has-text-primary'>
                        <Icon svg='picto-structure' /> Ajouter un lieu
                      </NavLink>
                      ]
                      )
                  }
              </li>,
            ]
          )
          }
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
    const selectManagedVenues = createSelectManagedVenues()
    const selectManagedOccasions = createSelectManagedOccasions(selectManagedVenues)
    return (state, ownProps) => ({
      managedOccasions: selectManagedOccasions(state, ownProps),
      managedVenues: selectManagedVenues(state, ownProps),
    })
  }
) (OffererItem)
