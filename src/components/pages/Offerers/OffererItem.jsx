import { Icon, pluralize } from 'pass-culture-shared'
import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import selectPhysicalVenuesByOffererId from '../../../selectors/selectPhysicalVenuesByOffererId'
import selectVenuesByOffererIdAndOfferType from '../../../selectors/selectVenuesByOffererIdAndOfferType'

const OffererItem = ({ offerer, physicalVenues, venues }) => {
  const { id, name, nOffers, isValidated } = offerer || {}

  const showPath = `/structures/${id}`

  const $offersCount =
    nOffers && nOffers > 0 ? (
      <li>
        <NavLink to={`/offres?structure=${id}`} className="has-text-primary">
          <Icon svg="ico-offres-r" />
          {pluralize(nOffers, 'offres')}
        </NavLink>
      </li>
    ) : (
      <li>0 offre</li>
    )

  const canCreateOnlyVirtualOffer = venues.length === 1 && venues[0].isVirtual

  const $offerActions = venues.length ? (
    // J'ai déja ajouté Un lieu mais pas d'offres
    <Fragment>
      <li>
        <NavLink
          to={`/offres/creation?structure=${id}`}
          className="has-text-primary">
          <Icon svg="ico-offres-r" />
          Nouvelle offre {canCreateOnlyVirtualOffer && 'numérique'}
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
        {pluralize(physicalVenues.length, 'lieux')}
      </li>
      <li>
        <NavLink
          to={`/structures/${id}/lieux/creation`}
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
          <p className="is-italic mb12" id="offerer-item-validation">
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

function mapStateToProps(state, ownProps) {
  const offererId = ownProps.offerer.id
  return {
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererIdAndOfferType(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
