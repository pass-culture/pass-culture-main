import { Icon, pluralize } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'

const OffererItem = ({ offerer, physicalVenues, venues }) => {
  const { id, name, nOffers, isValidated } = offerer || {}

  const showPath = `/structures/${id}`

  const $offersCount =
    nOffers && nOffers > 0 ? (
      <li>
        <NavLink
          className="has-text-primary"
          to={`/offres?structure=${id}`}
        >
          <Icon svg="ico-offres-r" />
          {pluralize(nOffers, 'offres')}
        </NavLink>
      </li>
    ) : (
      <li>{"0 offre"}</li>
    )

  const canCreateOnlyVirtualOffer = venues.length === 1 && venues[0].isVirtual

  const $offerActions = venues.length ? (
    // J'ai déja ajouté Un lieu mais pas d'offres
    <Fragment>
      <li>
        <NavLink
          className="has-text-primary"
          to={`/offres/creation?structure=${id}`}
        >
          <Icon svg="ico-offres-r" />
          Nouvelle offre {canCreateOnlyVirtualOffer && 'numérique'}
        </NavLink>
      </li>
      {$offersCount}
    </Fragment>
  ) : (
    <li
      className="is-italic"
      key={0}
    >
      {"Créez un lieu pour pouvoir y associer des offres."}
    </li>
  )

  // J'ai ajouté un lieu
  const $venueActions = (
    <Fragment>
      <li>
        <Icon svg="ico-venue" />
        {pluralize(physicalVenues.length, 'lieux')}
      </li>
      <li>
        <NavLink
          className="has-text-primary"
          to={`/structures/${id}/lieux/creation`}
        >
          <Icon svg="ico-venue-r" />{"Nouveau lieu"}
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
          <p
            className="is-italic mb12"
            id="offerer-item-validation"
          >
            {"Structure en cours de validation par l'équipe Pass Culture."}
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

OffererItem.defaultProps = {
  physicalVenues: [],
  venues: [],
}

OffererItem.propTypes = {
  physicalVenues: PropTypes.arrayOf,
  venues: PropTypes.arrayOf,
}

export default OffererItem
