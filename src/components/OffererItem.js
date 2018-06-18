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
  offerer: {
    id,
    address,
    name,
    isActive,
  }
}) => {
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
          <li>
            <NavLink to={`/offres?offererId=${id}`} className='has-text-primary'>
              <Icon svg='ico-offres-r' />
              {
                get(managedOccasions, 'length')
                  ? `${managedOccasions.length} offres`
                  : '0 offre'
              }
            </NavLink>
          </li>
          <li>
            <NavLink to={showPath}>
              <Icon svg='picto-structure' />
              {
                get(managedVenues, 'length')
                  ? `${managedVenues.length} lieux`
                  : '0 lieu'
              }
            </NavLink>
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
    const selectManagedVenues = createSelectManagedVenues()
    const selectManagedOccasions = createSelectManagedOccasions(selectManagedVenues)
    return (state, ownProps) => ({
      managedOccasions: selectManagedOccasions(state, ownProps),
      managedVenues: selectManagedVenues(state, ownProps),
    })
  }
) (OffererItem)
