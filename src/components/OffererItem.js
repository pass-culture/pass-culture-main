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
              // J'ai déja ajouté Un lieu mais pas d'offres
              get(managedVenues, 'length') > 0  ?
              (
              [
                <li>
                  <NavLink to={`/offres/nouveau`} className='has-text-primary'>
                    <Icon svg='ico-offres-r' />
                    Nouvelle offre
                  </NavLink>
                </li>,
                // J'ai au moins 1 offre
                get(managedOccasions, 'length') > 0 &&
                  <li>
                    <NavLink to={`/offres?offererId=${id}`} className='has-text-primary'>
                      <Icon svg='ico-offres-r' />
                      { managedOccasions.length === 1 ?  (`${managedOccasions.length} offre`) :
                      (`${managedOccasions.length} offres`)}
                    </NavLink>
                  </li>,
                get(managedOccasions, 'length') === 0 &&
                <li>0 offre</li>
              ]
              ) : (
                <li className='is-italic'>Créez un lieu pour pouvoir y associer des offres.</li>
              ),
              // J'ai ajouté un lieu
              get(managedVenues, 'length')  > 0 ?
              (
                <li>
                  <NavLink to={showPath}>
                    <Icon svg='ico-offres-r' />
                    { managedVenues.length === 1 ?  (`${managedVenues.length} lieu`) :
                    (`${managedVenues.length} lieux`)}
                  </NavLink>
                </li>
              ) :
              // je n'ai pas encore ajouté de lieu
              <li>
                <NavLink to={`/structures/${get(offerer, 'id')}/lieux/nouveau`}
                className='has-text-primary'>
                <Icon svg='picto-structure' /> Ajouter un lieu
              </NavLink>
              </li>
          ])
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
