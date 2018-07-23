import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OccurenceForm from './OccurenceForm'
import { mergeFormData } from '../reducers/form'
import { closeModal } from '../reducers/modal'
import eventSelector from '../selectors/event'
import occasionSelector from '../selectors/occasion'
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
      event,
      eventOccurenceId,
      provider,
      occasion,
      occurences,
    } = this.props

    return (
      <div className='occurence-manager'>
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
              {
                eventOccurenceId === 'nouvelle'
                ? (
                  <OccurenceForm
                    isEditing
                    isFullyEditable={!provider}
                    isNew
                    occurence={occurences[0]}
                  />
                )
                : (
                  <tr>
                    <td colSpan='10'>
                      {
                        provider
                        ? (
                          <i>
                            Il n'est pas possible d'ajouter ni de supprimer de dates pour cet événement {provider.name}
                          </i>
                        )
                        : (
                          <NavLink
                            className='button is-secondary'
                            to={`/offres/${get(occasion, 'id')}?gestion&date=nouvelle`}>
                            + Ajouter un horaire
                          </NavLink>
                        )
                      }
                    </td>
                  </tr>
                )
              }
              {
                occurences.map(o =>
                  <OccurenceForm
                    key={o.id}
                    isFullyEditable={!provider}
                    isEditing={o.id === eventOccurenceId}
                    occurence={o} />)
              }
            </tbody>
            {occurences.length > 12 && (
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
      const { eventOccurenceId } = (search || {})
      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { eventId, venueId } = (occasion || {})
      const event = eventSelector(state, eventId)
      const occurences = occurencesSelector(state, venueId, eventId)
      return {
        event,
        eventOccurenceId,
        occasion,
        occurences,
        provider: providerSelector(state, get(event, 'lastProviderId'))
      }
    },
    { closeModal, mergeFormData }
  )
)(OccurenceManager)
