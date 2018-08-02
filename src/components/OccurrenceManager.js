import get from 'lodash.get'
import { closeModal, mergeForm } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OccurrenceForm from './OccurrenceForm'
import eventSelector from '../selectors/event'
import occurrenceErrorsSelector from '../selectors/occurrenceErrors'
import occurrencesSelector from '../selectors/occurrences'
import offerSelector from '../selectors/offer'
import searchSelector from '../selectors/search'
import providerSelector from '../selectors/provider'

class OccurrenceManager extends Component {
  onCloseClick = e => {
    const { offer, history, closeModal } = this.props
    closeModal()
    history.push(`/offres/${get(offer, 'id')}`)
  }

  render() {
    const {
      errors,
      event,
      eventOccurrenceIdOrNew,
      isEditing,
      location,
      provider,
      offer,
      occurrences,
    } = this.props

    return (
      <div className="occurrence-manager">
        {errors && (
          <div className="notification is-danger">
            {Object.keys(errors).map(key => (
              <p key={key}>
                {' '}
                {key} : {errors[key]}
              </p>
            ))}
          </div>
        )}
        <div className="occurrence-table-wrapper">
          <div className="subtitle has-text-weight-bold has-text-left is-uppercase">
            {get(event, 'name')}
          </div>
          <div className="main-title has-text-left">
            Dates, horaires et prix
          </div>
          <table className="table is-hoverable occurrence-table">
            <thead>
              <tr>
                <td>Date</td>
                <td>Heure de début</td>
                <td>Heure de fin</td>
                <td>Prix</td>
                <td>Date Limite de Réservation</td>
                <td>Places (total)</td>
                <td>Supprimer</td>
                <td>Modifier</td>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan="10">
                  {provider ? (
                    <i>
                      Il n'est pas possible d'ajouter ni de supprimer d'horaires
                      pour cet événement {provider.name}
                    </i>
                  ) : (
                    <NavLink
                      className="button is-secondary"
                      disabled={isEditing}
                      to={
                        isEditing
                          ? `${location.pathname}${location.search}`
                          : `/offres/${get(offer, 'id')}?gestion&date=nouvelle`
                      }>
                      + Ajouter un horaire
                    </NavLink>
                  )}
                </td>
              </tr>
              {eventOccurrenceIdOrNew === 'nouvelle' && (
                <OccurrenceForm isFullyEditable={!provider} />
              )}
              {occurrences.map(o => (
                <OccurrenceForm
                  key={o.id}
                  isFullyEditable={!provider}
                  occurrence={o}
                />
              ))}
            </tbody>
            {occurrences.length > 12 && (
              <thead>
                <tr>
                  <td>Date</td>
                  <td>Heure de début</td>
                  <td>Heure de fin</td>
                  <td>Prix</td>
                  <td>Date Limite de Réservation</td>
                  <td>Places (total)</td>
                  <td>Supprimer</td>
                  <td>Modifier</td>
                </tr>
              </thead>
            )}
          </table>
        </div>
        <button
          className="button is-secondary is-pulled-right"
          onClick={this.onCloseClick}>
          Fermer
        </button>
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const search = searchSelector(state, ownProps.location.search)
      const { eventOccurrenceIdOrNew, stockIdOrNew } = search || {}
      const isEditing = eventOccurrenceIdOrNew || stockIdOrNew

      const offer = offerSelector(state, ownProps.match.params.offerId)
      const { eventId, venueId } = offer || {}
      const event = eventSelector(state, eventId)
      const occurrences = occurrencesSelector(state, venueId, eventId)

      const errors = occurrenceErrorsSelector(state)

      return {
        errors,
        event,
        eventOccurrenceIdOrNew,
        isEditing,
        occurrences,
        offer,
        provider: providerSelector(state, get(event, 'lastProviderId')),
      }
    },
    { closeModal, mergeForm }
  )
)(OccurrenceManager)
