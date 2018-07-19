import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import OccurenceForm from './OccurenceForm'
import OccurenceItem from './OccurenceItem'
import { mergeForm } from '../reducers/form'
import { closeModal } from '../reducers/modal'
import eventSelector from '../selectors/event'
import occasionSelector from '../selectors/occasion'
import occurencesSelector from '../selectors/occurences'
import providerSelector from '../selectors/provider'
import timezoneSelector from '../selectors/timezone'
import { queryStringToObject } from '../utils/string'

class OccurenceManager extends Component {

  newOccurenceWithDefaults(occurence) {
    if (!occurence) return
    const beginningDatetime = moment(occurence.beginningDatetime).tz(this.props.tz).add(1, 'days')
    const endDatetime = moment(occurence.endDatetime).tz(this.props.tz).add(1, 'days').format('HH:mm')

    const newOccurence = {
      beginningDatetime,
      endDatetime,
      ...get(occurence, 'offer.0',{}),
    }
    return newOccurence
  }

  render() {
    const {
      event,
      location: {search},
      provider,
      occasion,
      occurences,
    } = this.props

    const eventOccurenceId = queryStringToObject(search).dates

    console.log('occasion', occasion)

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
              { eventOccurenceId === 'nouvelle' ? (
                <OccurenceForm
                  isEditable={!provider}
                  occurence={this.newOccurenceWithDefaults(occurences[0])}
                />
              ) : (
                <tr>
                  <td colSpan='10'>
                    { provider ? (
                      <i>
                        Il n'est pas possible d'ajouter ni de supprimer de dates pour cet événement {provider.name}
                      </i>
                    ) : (
                      <NavLink to={`/offres/${get(occasion, 'id')}?dates=nouvelle`} className='button is-secondary'>
                        + Ajouter un horaire
                      </NavLink>
                    )}
                  </td>
                </tr>
              )}
              { occurences.map(o =>
                o.id === eventOccurenceId && !provider ?
                <OccurenceForm
                  key={o.id}
                  isEditable={!provider}
                  occurence={o}
                /> :
                <OccurenceItem
                  key={o.id}
                  isEditable={!provider}
                  occurence={o}
                />
              )}
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
          onClick={e => (this.props.closeModal() && this.props.history.push(`/offres/${get(occasion, 'id')}`))}
          to={`/offres/${get(occasion, 'id')}`}
          className="button is-secondary is-pulled-right">
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
      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { eventId, venueId } = (occasion || {})
      const event = eventSelector(state, eventId)
      const occurences = occurencesSelector(state, venueId, eventId)
      return {
        event,
        occasion,
        occurences,
        provider: providerSelector(state, get(event, 'lastProviderId')),
        tz: timezoneSelector(state, venueId),
      }
    },
    { closeModal, mergeForm }
  )
)(OccurenceManager)
