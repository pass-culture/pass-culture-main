import classnames from 'classnames'
import get from 'lodash.get'
import { closeModal } from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import EventOccurrenceAndStockItem from '../items/EventOccurrenceAndStockItem'
import eventSelector from '../../selectors/event'
import eventOccurrencesSelector from '../../selectors/eventOccurrences'
import occurrenceErrorsSelector from '../../selectors/occurrenceErrors'
import offerSelector from '../../selectors/offer'
import searchSelector from '../../selectors/search'
import thingSelector from '../../selectors/thing'
import providerSelector from '../../selectors/provider'
import stocksSelector from '../../selectors/stocks'

class EventOccurrencesAndStocksManager extends Component {
  onCloseClick = e => {
    const { dispatch, offer, history } = this.props
    dispatch(closeModal())
    history.push(`/offres/${get(offer, 'id')}`)
  }

  render() {
    const {
      errors,
      event,
      eventOccurrences,
      isEditing,
      isNew,
      location,
      provider,
      offer,
      stocks,
      thing,
    } = this.props
    const isStockOnly = typeof get(thing, 'id') !== 'undefined'

    return (
      <div className="event-occurrences-and-stocks-manager">
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
        <div className="event-occurrences-and-stocks-table-wrapper">
          <div className="subtitle has-text-weight-bold has-text-left is-uppercase">
            {get(event, 'name')}
          </div>
          <div className="main-title has-text-left">
            {get(event, 'id') && 'Dates, horaires et prix'}
            {get(thing, 'id') && 'Prix'}
          </div>
          <table
            className={classnames(
              'table is-hoverable event-occurrences-and-stocks-table',
              { small: isStockOnly }
            )}>
            <thead>
              <tr>
                {!isStockOnly && (
                  <Fragment>
                    <td>Date</td>
                    <td>
                      Heure de<br />début
                    </td>
                    <td>
                      Heure de<br />fin
                    </td>
                  </Fragment>
                )}
                <td>Prix</td>
                {!isStockOnly && <td>Date Limite de Réservation</td>}
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
                          : isStockOnly
                            ? `/offres/${get(
                                offer,
                                'id'
                              )}?gestion&stock=nouveau`
                            : `/offres/${get(
                                offer,
                                'id'
                              )}?gestion&date=nouvelle`
                      }>
                      {isStockOnly
                        ? '+ Ajouter un prix'
                        : '+ Ajouter un horaire'}
                    </NavLink>
                  )}
                </td>
              </tr>
              {isNew && (
                <EventOccurrenceAndStockItem
                  isFullyEditable={!provider}
                  isStockOnly={isStockOnly}
                />
              )}
              {(isStockOnly ? stocks : eventOccurrences).map(item => (
                <EventOccurrenceAndStockItem
                  key={item.id}
                  isFullyEditable={!provider}
                  isStockOnly={isStockOnly}
                  {...{ [isStockOnly ? 'stock' : 'eventOccurrence']: item }}
                />
              ))}
            </tbody>
            {eventOccurrences.length > 12 && (
              <thead>
                <tr>
                  {!isStockOnly && (
                    <Fragment>
                      <td>Date</td>
                      <td>Heure de début</td>
                      <td>Heure de fin</td>
                    </Fragment>
                  )}
                  <td>Prix</td>
                  {!isStockOnly && <td>Date Limite de Réservation</td>}
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
  connect((state, ownProps) => {
    const search = searchSelector(state, ownProps.location.search)
    const { eventOccurrenceIdOrNew, stockIdOrNew } = search || {}

    const isEditing = eventOccurrenceIdOrNew || stockIdOrNew
    const isNew =
      eventOccurrenceIdOrNew === 'nouvelle' ||
      (!eventOccurrenceIdOrNew && stockIdOrNew === 'nouveau')

    const offerId = ownProps.match.params.offerId
    const offer = offerSelector(state, offerId)

    const eventId = get(offer, 'eventId')
    const event = eventSelector(state, eventId)
    const eventOccurrences = eventOccurrencesSelector(
      state,
      ownProps.match.params.offerId
    )

    const thingId = get(offer, 'thingId')
    const thing = thingSelector(state, thingId)

    console.log('EO', eventOccurrences)
    const stocks = stocksSelector(state, offerId, eventOccurrences)

    const errors = occurrenceErrorsSelector(state)

    return {
      errors,
      event,
      eventOccurrenceIdOrNew,
      eventOccurrences,
      isEditing,
      isNew,
      offer,
      provider: providerSelector(state, get(event, 'lastProviderId')),
      stocks,
      thing,
    }
  })
)(EventOccurrencesAndStocksManager)
