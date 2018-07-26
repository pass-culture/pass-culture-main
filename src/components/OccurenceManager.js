import { mergeFormData } from 'pass-culture-shared'
// import { mergeFormData } from 'shared/reducers/form'

import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OccurenceForm from './OccurenceForm'
import { closeModal } from '../reducers/modal'
import eventSelector from '../selectors/event'
import occasionSelector from '../selectors/occasion'
import occurenceErrorsSelector from '../selectors/occurenceErrors'
import occurencesSelector from '../selectors/occurences'
import searchSelector from '../selectors/search'
import providerSelector from '../selectors/provider'
import timezoneSelector from '../selectors/timezone'


class OccurenceManager extends Component {

  onCloseClick = e => {
    const {
      occasion,
      history,
      closeModal,
    } = this.props
    closeModal()
    history.push(`/offres/${get(occasion, 'id')}`)
  }

  render() {
    const {
      errors,
      event,
      eventOccurenceIdOrNew,
      isEditing,
      location,
      provider,
      occasion,
      occurences,
    } = this.props

    return (
      <div className='occurence-manager'>
        {
          errors && (
            <div className='notification is-danger'>
            {
              Object.keys(errors).map(key =>
                <p key={key}> {key} : {errors[key]}</p>
              )
            }
            </div>
          )
        }
        <div className='occurence-table-wrapper'>
          <div className='subtitle has-text-weight-bold has-text-left is-uppercase'>
            {get(event, 'name')}
          </div>
          <div className="pc-title has-text-left">
            Dates, horaires et prix
          </div>
          <table className='table is-hoverable occurence-table'>
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
                <td colSpan='10'>
                  {
                    provider
                      ? (
                        <i>
                          Il n'est pas possible d'ajouter ni de supprimer d'horaires pour cet événement {provider.name}
                        </i>
                      )
                      : (
                        <NavLink
                          className='button is-secondary'
                          disabled={isEditing}
                          to={
                            isEditing
                              ? `${location.pathname}${location.search}`
                              : `/offres/${get(occasion, 'id')}?gestion&date=nouvelle`
                          }>
                          + Ajouter un horaire
                        </NavLink>
                      )
                  }
                </td>
              </tr>
              {
                eventOccurenceIdOrNew === "nouvelle" &&
                <OccurenceForm isFullyEditable={!provider} />
              }
              {
                occurences.map(o =>
                  <OccurenceForm
                    key={o.id}
                    isFullyEditable={!provider}
                    occurence={o} />)
              }
            </tbody>
            {
              occurences.length > 12 && (
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
              )
            }
          </table>
        </div>
        <button
          className="button is-secondary is-pulled-right"
          onClick={this.onCloseClick} >
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
      const { eventOccurenceIdOrNew, offerIdOrNew } = (search || {})
      const isEditing = eventOccurenceIdOrNew || offerIdOrNew

      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { eventId, venueId } = (occasion || {})
      const event = eventSelector(state, eventId)
      const occurences = occurencesSelector(state, venueId, eventId)

      const errors = occurenceErrorsSelector(state)

      return {
        errors,
        event,
        eventOccurenceIdOrNew,
        isEditing,
        occasion,
        occurences,
        provider: providerSelector(state, get(event, 'lastProviderId'))
      }
    },
    { closeModal, mergeFormData }
  )
)(OccurenceManager)
