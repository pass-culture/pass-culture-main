import { Icon } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import venuesSelector from '../../../selectors/venues'
import { pluralize } from '../../../utils/string'

const OffererItemActions = ({ offerer, venues }) => {
  const { id, nOffers } = offerer || {}

  const $offersCount =
    nOffers > 0 ? (
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
  const $venueActions = venues.length ? (
    <li>
      <Icon svg="ico-venue" />
      {pluralize(venues.length, 'lieux')}
    </li>
  ) : (
    // je n'ai pas encore ajouté de lieu
    <li>
      <NavLink
        to={`/structures/${id}/lieux/nouveau`}
        className="has-text-primary">
        <Icon svg="ico-venue-r" /> Ajouter un lieu
      </NavLink>
    </li>
  )

  return (
    <Fragment>
      {$offerActions}
      {$venueActions}
    </Fragment>
  )
}

export default connect(() => {
  return (state, ownProps) => ({
    venues: venuesSelector(state, ownProps.offerer.id),
  })
})(OffererItemActions)
