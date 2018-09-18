import classnames from 'classnames'
import get from 'lodash.get'
import {
  Field,
  Form,
  Icon,
  mergeForm,
  requestData,
  resetForm,
  SubmitButton,
} from 'pass-culture-shared'
import moment from 'moment'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { Portal } from 'react-portal'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import eventSelector from '../../selectors/event'
import eventOccurrencePatchSelector from '../../selectors/eventOccurrencePatch'
import eventOccurrencesSelector from '../../selectors/eventOccurrences'
import offerSelector from '../../selectors/offer'
import searchSelector from '../../selectors/search'
import stockSelector from '../../selectors/stock'
import stockPatchSelector from '../../selectors/stockPatch'
import timezoneSelector from '../../selectors/timezone'
import venueSelector from '../../selectors/venue'

class EventOccurrenceAndStockItem extends Component {
  constructor() {
    super()
    this.state = {
      $submit: null,
      isDeleting: false,
    }
  }

  onDeleteClick = () => {
    this.setState({ isDeleting: true })
  }

  onCancelDeleteClick = () => {
    this.setState({ isDeleting: false })
  }

  onConfirmDeleteClick = () => {
    const {
      dispatch,
      eventOccurrencePatch,
      isStockOnly,
      stockPatch,
    } = this.props
    dispatch(
      requestData(
        'DELETE',
        isStockOnly
          ? `stocks/${stockPatch.id}`
          : `eventOccurrences/${eventOccurrencePatch.id}`
      )
    )
  }

  handleCrossingEndDatetime = () => {
    const {
      dispatch,
      eventOccurrencePatch,
      formBeginningDatetime,
      formEndDatetime,
      isStockOnly,
    } = this.props
    if (isStockOnly) {
      return
    }
    if (formEndDatetime < formBeginningDatetime) {
      dispatch(
        mergeForm(`eventOccurrence${get(eventOccurrencePatch, 'id', '')}`, {
          endDatetime: moment(formEndDatetime)
            .add(1, 'day')
            .toISOString(),
        })
      )
    }
  }

  handleEventOccurrenceSuccessData = (state, action) => {
    const { history, offer, stockPatch } = this.props
    const stockIdOrNew = get(stockPatch, 'id', 'nouveau')
    history.push(
      `/offres/${get(offer, 'id')}?gestion&date=${
        action.data.id
      }&stock=${stockIdOrNew}`
    )
  }

  handleInitBookingLimitDatetime = () => {
    const {
      dispatch,
      eventOccurrencePatch,
      formBookingLimitDatetime,
      isStockOnly,
      isStockReadOnly,
      stockPatch,
    } = this.props
    if (
      isStockOnly ||
      !get(eventOccurrencePatch, 'id') ||
      formBookingLimitDatetime ||
      isStockReadOnly
    ) {
      return
    }
    dispatch(
      mergeForm(`stock${get(stockPatch, 'id', '')}`, {
        bookingLimitDatetime: moment(eventOccurrencePatch.beginningDatetime)
          .subtract(2, 'day')
          .toISOString(),
      })
    )
  }

  handleInitEndDatetime = () => {
    const {
      dispatch,
      eventOccurrencePatch,
      formBeginningDatetime,
      isStockOnly,
    } = this.props
    if (isStockOnly || get(eventOccurrencePatch, 'id')) {
      return
    }
    dispatch(
      mergeForm(`eventOccurrence${get(eventOccurrencePatch, 'id', '')}`, {
        endDatetime: moment(formBeginningDatetime)
          .add(1, 'hour')
          .toISOString(),
      })
    )
  }

  handleInitPrice = () => {
    const { dispatch, formPrice, stockPatch } = this.props
    if (get(stockPatch, 'id') || typeof formPrice !== 'undefined') {
      return
    }
    dispatch(mergeForm(`stock${get(stockPatch, 'id', '')}`, { price: 0 }))
  }

  handleNextDatetimes = () => {
    const {
      dispatch,
      eventOccurrencePatch,
      eventOccurrences,
      formBeginningDatetime,
      isStockOnly,
    } = this.props
    // add automatically a default beginninDatetime and a endDatetime
    // one day after the previous eventOccurrence
    if (isStockOnly || get(eventOccurrencePatch, 'id')) {
      return
    }
    if (!formBeginningDatetime && get(eventOccurrences, 'length')) {
      const beginningDatetime = moment(
        eventOccurrences[0].beginningDatetime
      ).add(1, 'day')
      dispatch(
        mergeForm(`eventOccurrence${get(eventOccurrencePatch, 'id', '')}`, {
          beginningDatetime,
          endDatetime: moment(beginningDatetime).add(1, 'hour'),
        })
      )
    }
  }

  handleOfferSuccessData = (state, action) => {
    const { history, offer } = this.props
    history.push(`/offres/${get(offer, 'id')}?gestion`)
  }

  handleResetForm = () => {
    const { dispatch, isEditing } = this.props
    if (!isEditing) {
      dispatch(resetForm())
    }
  }

  componentWillMount() {
    this.handleResetForm()
  }

  componentDidMount() {
    this.setState({ $submit: this.$submit })
    this.handleNextDatetimes()
    this.handleInitBookingLimitDatetime()
    this.handleInitPrice()
  }

  componentDidUpdate(prevProps) {
    const { formBeginningDatetime, isEditing } = this.props

    if (prevProps.isEditing && !isEditing) {
      this.handleResetForm()
    }

    this.handleNextDatetimes()
    this.handleInitBookingLimitDatetime()
    this.handleCrossingEndDatetime()

    if (formBeginningDatetime && !prevProps.formBeginningDatetime) {
      this.handleInitEndDatetime()
    }

    this.handleInitPrice()
  }

  render() {
    const {
      eventOccurrencePatch,
      eventOccurrences,
      formBeginningDatetime,
      isEditing,
      isEventOccurrenceReadOnly,
      isStockOnly,
      isStockReadOnly,
      offer,
      stockPatch,
      tz,
    } = this.props
    const { isDeleting } = this.state

    const beginningDatetime =
      formBeginningDatetime || get(eventOccurrencePatch, 'beginningDatetime')

    return (
      <Fragment>
        <tr
          className={classnames('event-occurrence-and-stock-item', {
            'with-confirm': isDeleting,
          })}>
          {!isStockOnly && (
            <Form
              action={`/eventOccurrences/${get(
                eventOccurrencePatch,
                'id',
                ''
              )}`}
              BlockComponent={null}
              handleSuccess={this.handleEventOccurrenceSuccessData}
              layout="input-only"
              name={`eventOccurrence${get(eventOccurrencePatch, 'id', '')}`}
              patch={eventOccurrencePatch}
              readOnly={isEventOccurrenceReadOnly}
              size="small"
              Tag={null}>
              <td>
                <Field name="offerId" type="hidden" />
                <Field name="venueId" type="hidden" />
                <Field
                  minDate={beginningDatetime}
                  name="endDatetime"
                  type="hidden"
                />
                <Field
                  debug
                  highlightedDates={eventOccurrences.map(
                    eo => eo.beginningDatetime
                  )}
                  minDate="today"
                  name="beginningDate"
                  patchKey="beginningDatetime"
                  readOnly={isEventOccurrenceReadOnly}
                  required
                  title="Date"
                  type="date"
                  tz={tz}
                />
              </td>
              <td>
                <Field
                  name="beginningTime"
                  patchKey="beginningDatetime"
                  readOnly={isEventOccurrenceReadOnly}
                  required
                  title="Heure"
                  type="time"
                  tz={tz}
                />
              </td>
              <td>
                <Field
                  name="endTime"
                  patchKey="endDatetime"
                  readOnly={isEventOccurrenceReadOnly}
                  required
                  title="Heure de fin"
                  type="time"
                  tz={tz}
                />
              </td>
              {!isEventOccurrenceReadOnly && (
                <Portal node={this.state.$submit}>
                  <SubmitButton className="button is-primary is-small">
                    Valider
                  </SubmitButton>
                </Portal>
              )}
            </Form>
          )}
          <Form
            action={`/stocks/${get(stockPatch, 'id', '')}`}
            BlockComponent={null}
            handleSuccess={this.handleOfferSuccessData}
            layout="input-only"
            key={1}
            name={`stock${get(stockPatch, 'id', '')}`}
            patch={stockPatch}
            size="small"
            readOnly={isStockReadOnly}
            Tag={null}>
            <td title="Vide si gratuit">
              <Field name="eventOccurrenceId" type="hidden" />
              <Field name="offerId" type="hidden" />
              <Field
                displayValue={(value, { readOnly }) =>
                  value === 0
                    ? readOnly
                      ? 'Gratuit'
                      : 0
                    : readOnly
                      ? `${value}€`
                      : value
                }
                name="price"
                placeholder="Gratuit"
                type="number"
                title="Prix"
              />
            </td>
            <td title="Laissez vide si pas de limite">
              <Field
                maxDate={beginningDatetime}
                name="bookingLimitDatetime"
                placeholder="Laissez vide si pas de limite"
                type="date"
              />
            </td>
            <td title="Laissez vide si pas de limite">
              <Field
                name="available"
                title="Places disponibles"
                type="number"
              />
            </td>
            {!isStockReadOnly && (
              <Portal node={this.state.$submit}>
                <SubmitButton className="button is-primary is-small">
                  Valider
                </SubmitButton>
              </Portal>
            )}
          </Form>
          <td className="is-clipped">
            {isEditing ? (
              <NavLink
                className="button is-secondary is-small"
                to={`/offres/${get(offer, 'id')}?gestion`}>
                Annuler
              </NavLink>
            ) : (
              <button
                className="button is-small is-secondary"
                style={{ width: '100%' }}
                onClick={this.onDeleteClick}>
                <span className="icon">
                  <Icon svg="ico-close-r" />
                </span>
              </button>
            )}
          </td>
          <td ref={_e => (this.$submit = _e)}>
            {!isEditing && (
              <NavLink
                to={`/offres/${get(offer, 'id')}?gestion&${
                  isStockOnly
                    ? `stock=${get(stockPatch, 'id')}`
                    : `date=${get(eventOccurrencePatch, 'id')}`
                }`}
                className="button is-small is-secondary">
                <span className="icon">
                  <Icon svg="ico-pen-r" />
                </span>
              </NavLink>
            )}
          </td>
        </tr>
        {isDeleting && (
          <tr>
            <td className="is-size-7" colSpan={isStockOnly ? '3' : '6'}>
              En confirmant l'annulation de{' '}
              {isStockOnly ? 'ce stock' : 'cette date'}, vous supprimerez aussi
              toutes les réservations associées. {!isStockOnly && <br />}Êtes-vous
              sûrs de vouloir continuer&nbsp;?
            </td>
            <td>
              <button
                className="button is-primary"
                onClick={this.onConfirmDeleteClick}>
                Oui
              </button>
            </td>
            <td>
              <button
                className="button is-primary"
                onClick={this.onCancelDeleteClick}>
                Non
              </button>
            </td>
          </tr>
        )}
      </Fragment>
    )
  }
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const search = searchSelector(state, ownProps.location.search)
    const { eventOccurrenceIdOrNew, stockIdOrNew } = search || {}

    const offerId = ownProps.match.params.offerId
    const offer = offerSelector(state, offerId)
    const { eventId, venueId } = offer || {}

    const eventOccurrencePatch = eventOccurrencePatchSelector(
      state,
      ownProps.eventOccurrence,
      ownProps.match.params.offerId,
      venueId
    )
    const eventOccurrenceId = get(eventOccurrencePatch, 'id')

    const isEventOccurrenceReadOnly =
      !eventOccurrenceIdOrNew ||
      (eventOccurrenceIdOrNew === 'nouvelle' && eventOccurrenceId) ||
      (eventOccurrenceIdOrNew !== 'nouvelle' &&
        eventOccurrenceId !== eventOccurrenceIdOrNew) ||
      stockIdOrNew ||
      !ownProps.isFullyEditable

    const venue = venueSelector(state, venueId)

    const stock = ownProps.isStockOnly
      ? ownProps.stock
      : stockSelector(state, offerId, get(ownProps, 'eventOccurrence'))

    const stockPatch = stockPatchSelector(
      state,
      stock,
      offerId,
      get(ownProps, 'eventOccurrence.id'),
      get(venue, 'managingOffererId')
    )

    const stockId = get(stock, 'id')

    const isStockReadOnly =
      (!ownProps.isStockOnly &&
        (!eventOccurrenceId ||
          !eventOccurrenceIdOrNew ||
          eventOccurrenceIdOrNew === 'nouvelle' ||
          eventOccurrenceIdOrNew !== eventOccurrenceId)) ||
      !stockIdOrNew ||
      (stockIdOrNew === 'nouveau' && stockId) ||
      (stockIdOrNew !== 'nouveau' && stockId !== stockIdOrNew)

    const isEditing = !isEventOccurrenceReadOnly || !isStockReadOnly

    return {
      event: eventSelector(state, eventId),
      eventId,
      eventOccurrencePatch,
      eventOccurrences: eventOccurrencesSelector(state, venueId, eventId),
      eventOccurrenceIdOrNew,
      formBeginningDatetime: get(
        state,
        `form.eventOccurrence${eventOccurrenceId || ''}.beginningDatetime`
      ),
      formBookingLimitDatetime: get(
        state,
        `form.stock${stockId || ''}.bookingLimitDatetime`
      ),
      formEndDatetime: get(
        state,
        `form.eventOccurrence${eventOccurrenceId || ''}.endDatetime`
      ),
      formPrice: get(state, `form.stock${stockId || ''}.price`),
      isEditing,
      isEventOccurrenceReadOnly,
      isStockReadOnly,
      offer,
      stockPatch,
      stockIdOrNew,
      tz: timezoneSelector(state, venueId),
      venue,
      venueId,
    }
  })
)(EventOccurrenceAndStockItem)
