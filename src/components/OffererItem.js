import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import createOccasionsSelector from '../selectors/createOccasions'
import createVenuesSelector from '../selectors/createVenues'
import { pluralize } from '../utils/string'

const OffererItem = ({
  occasions,
  offerer,
  venues,
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
            !isActive
              ? (
                <li className='is-italic'>En cours de validation : vous allez recevoir un e-mail.</li>
              )
              : [
              // J'ai déja ajouté Un lieu mais pas d'offres
              venues.length
                ? ([
                  <li key={0}>
                    <NavLink to={`/structures/${get(offerer, 'id')}/offres/nouveau`}
                      className='has-text-primary'>
                      <Icon svg='ico-offres-r' />
                      Nouvelle offre
                    </NavLink>
                  </li>,
                  // J'ai au moins 1 offre
                  occasions.length ? (
                    <li key={1}>
                      <NavLink to={`/offres?offererId=${id}`} className='has-text-primary'>
                        <Icon svg='ico-offres-r' />
                        { pluralize(occasions.length, 'offres') }
                      </NavLink>
                    </li>
                  ) : (
                    <li key={2}>0 offre</li>
                  )
                ])
                : (
                  <li className='is-italic' key={0}>Créez un lieu pour pouvoir y associer des offres.</li>
                ),
              // J'ai ajouté un lieu
              venues.length
              ? (
                  <li key={4}>
                    <NavLink to={showPath}>
                      <Icon svg='ico-offres-r' />
                      { pluralize(venues.length, 'lieux')}
                    </NavLink>
                  </li>
                )
              : (
                 // je n'ai pas encore ajouté de lieu
                <li key={4}>
                  <NavLink to={`/structures/${get(offerer, 'id')}/lieux/nouveau`}
                  className='has-text-primary'>
                    <Icon svg='picto-structure' /> Ajouter un lieu
                  </NavLink>
                </li>
              )
            ]
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

const occasionsSelector = createOccasionsSelector()
const venuesSelector = createVenuesSelector()

export default connect(
  () => {
    return (state, ownProps) => ({
      occasions: occasionsSelector(state, {offererId: ownProps.offerer.id}),
      venues: venuesSelector(state, {offererId: ownProps.offerer.id}),
    })
  }
) (OffererItem)
