import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import OccurenceItem from './OccurenceItem'
import { mergeForm } from '../reducers/form'
import { closeModal } from '../reducers/modal'
import createEventSelector from '../selectors/createEvent'
import createProviderSelector from '../selectors/createProvider'
import createTimezoneSelector from '../selectors/createTimezone'
import { NEW } from '../utils/config'

class OccurenceManager extends Component {

  onCloseClick = () => {
    const {
      closeModal,
      history,
      location,
      occasion
    } = this.props
    const {
      search
    } = location
    const {
      id
    } = (occasion || {})
    closeModal()
    id && history.push(`/offres/${id}${search}`)
  }

  onAddClick = () => {
    const {
      history,
      location,
      occasion
    } = this.props
    const {
      search
    } = location
    const {
      id
    } = (occasion || {})
    id && history.push(`/offres/${id}/dates/nouvelle${search}`)
  }

  handleNextData = () => {
    const {
      mergeForm,
      occurences,
      tz
    } = this.props

    const lastOccurence = occurences.length > 0 && occurences[0]
    if (lastOccurence) {
      const {
        beginningDatetime,
        endDatetime,
        offer
      } = lastOccurence
      const {
        available,
        groupSize,
        pmrGroupSize,
        price
      } = get(offer, '0', {})

      const date = moment(beginningDatetime).tz(tz).add(1, 'days')

      mergeForm('eventOccurences', NEW,
        {
          available,
          date,
          time: date.format('HH:mm'),
          endTime: moment(endDatetime).tz(tz).add(1, 'days').format('HH:mm'),
          groupSize,
          pmrGroupSize,
          price: typeof price === 'undefined'
            ? 0
            : price
        })
    }
  }

  componentDidMount () {
    const {
      match: { params: { eventOccurenceId } }
    } = this.props
    if (eventOccurenceId === 'nouvelle') {
      this.handleNextData()
    }
  }

  componentDidUpdate (prevProps) {
    const {
      match: { params: { eventOccurenceId } },
      occasion
    } = this.props
    const {
      id
    } = (occasion || {})
    if (eventOccurenceId === 'nouvelle' &&
      (
        eventOccurenceId !== get(prevProps, 'match.params.eventOccurenceId') ||
        (id && get(prevProps, 'occasion.id'))
      )
    ) {
      this.handleNextData()
    }
  }

  render() {
    const {
      event,
      history,
      location,
      match,
      provider,
      occasion,
      occurences,
    } = this.props
    const {
      name
    } = (event || {})
    const {
      params: { eventOccurenceId }
    } = match

    return (
      <div className='occurence-manager'>
        <div className='occurence-table-wrapper'>
          <div className='subtitle has-text-weight-bold has-text-left'>
            {name && name.toUpperCase()}
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
                {false && <td>Taille groupe</td>}
                {false && <td>Dont (PMR)</td>}
                <td>Supprimer</td>
                <td>Modifier</td>
              </tr>
            </thead>
            <tbody>
              {
                eventOccurenceId === 'nouvelle'
                  ? (
                    <OccurenceForm
                      history={history}
                      occasion={occasion}
                    />
                  ) : (
                  <tr><td colSpan='10'>
                    {
                      provider
                        ? (
                          <i>
                            Il n'est pas possible d'ajouter ni de supprimer de dates pour cet événement {provider.name}
                          </i>
                        )
                        : (
                          <button className='button is-secondary' onClick={this.onAddClick}>
                            + Ajouter un horaire
                          </button>
                        )
                    }
                  </td></tr>
                )
              }
              {
                occurences && occurences.map(o =>
                  <OccurenceItem
                    key={o.id}
                    history={history}
                    location={location}
                    match={match}
                    occasion={occasion}
                    occurence={o}
                    occurences={occurences}
                    provider={provider}
                  />
                )
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
                  {false && <td>Taille groupe</td>}
                  {false && <td>Dont PMR</td>}
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

const eventSelector = createEventSelector()
const providerSelector = createProviderSelector()
const timezoneSelector = createTimezoneSelector()

export default connect(
  (state, ownProps) => {
    const event = eventSelector(state, get(ownProps, 'occasion.eventId'))
    const venueId = get(ownProps, 'occasion.venueId')
    return {
      event,
      provider: providerSelector(state, get(event, 'lastProviderId')),
      tz: timezoneSelector(state, venueId),
    }
  },
  { closeModal, mergeForm }
)(OccurenceManager)
