import { Icon } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import venuesSelector from '../../../selectors/venues'
import { pluralize } from '../../../utils/string'

const OffererItem = ({ offerer, venues }) => {
  const { id, name, nOffers, isValidated } = offerer || {}

  const showPath = `/structures/${id}`

  const $offersCount =
    isValidated && nOffers > 0 ? (
      <li>
        <NavLink to={`/offres?structure=${id}`} className="has-text-primary">
          <Icon svg="ico-offres-r" />
          {pluralize(nOffers, 'offres')}
        </NavLink>
      </li>
    ) : (
      <li>0 offre</li>
    )

  const $offerActions = venues.length ? (
    // J'ai déja ajouté Un lieu mais pas d'offres
    <Fragment>
      <li>
        <NavLink
          to={`/offres/nouveau?structure=${id}`}
          className="has-text-primary">
          <Icon svg="ico-offres-r" />
          Nouvelle offre
        </NavLink>
      </li>
      {$offersCount}
    </Fragment>
  ) : (
    <li className="is-italic" key={0}>
      Créez un lieu pour pouvoir y associer des offres.
    </li>
  )

  // J'ai ajouté un lieu
  const $venueActions = (
    <Fragment>
      <li>
        <Icon svg="ico-venue" />
        {pluralize(venues.length, 'lieux')}
      </li>
      <li>
        <NavLink
          to={`/structures/${id}/lieux/nouveau`}
          className="has-text-primary">
          <Icon svg="ico-venue-r" /> Nouveau lieu
        </NavLink>
      </li>
    </Fragment>
  )

  return (
    <li className="offerer-item">
      <div className="list-content">
        <p className="name">
          <NavLink to={showPath}>{name}</NavLink>
        </p>
        {!isValidated && (
          <p className="is-italic mb12">
            Structure en cours de validation par l&apos;équipe Pass Culture.
          </p>
        )}
        <ul className="actions">
          {$offerActions}
          {$venueActions}
        </ul>
      </div>
      <div className="caret">
        <NavLink to={showPath}>
          <Icon svg="ico-next-S" />
        </NavLink>
      </div>
    </li>
  )
}

export default connect(() => {
  return (state, ownProps) => ({
    venues: venuesSelector(state, ownProps.offerer.id),
  })
})(OffererItem)
