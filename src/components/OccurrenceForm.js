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
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Portal } from 'react-portal'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import eventSelector from '../selectors/event'
import occurrenceSelector from '../selectors/occurrence'
import occurrencesSelector from '../selectors/occurrences'
import offerSelector from '../selectors/offer'
import searchSelector from '../selectors/search'
import stockSelector from '../selectors/stock'
import timezoneSelector from '../selectors/timezone'
import venueSelector from '../selectors/venue'

class OccurrenceForm extends Component {
  constructor() {
    super()
    this.state = {
      $submit: null,
    }
  }

  onDeleteClick = () => {
    const { occurrence, stock, isFullyEditable, requestData } = this.props

    // IF AN OFFER IS ASSOCIATED WE NEED TO DELETE IT FIRST
    if (get(stock, 'id')) {
      requestData('DELETE', `stocks/${stock.id}`, {
        key: 'stocks',
        handleSuccess: () => {
          isFullyEditable &&
            requestData('DELETE', `eventOccurrences/${occurrence.id}`, {
              key: 'eventOccurrences',
            })
        },
      })
    } else if (isFullyEditable) {
      requestData('DELETE', `eventOccurrences/${occurrence.id}`, {
        key: 'eventOccurrences',
      })
    }
  }

  handleCrossingEndDatetime = () => {
    const { formBeginningDatetime, formEndDatetime, mergeForm } = this.props
    if (formEndDatetime < formBeginningDatetime) {
      mergeForm('occurrence', {
        endDatetime: moment(formEndDatetime)
          .add(1, 'day')
          .toISOString(),
      })
    }
  }

  handleEventOccurrenceSuccessData = (state, action) => {
    const { history, offer, stock } = this.props
    const stockIdOrNew = get(stock, 'id', 'nouveau')
    history.push(
      `/offres/${get(offer, 'id')}?gestion&date=${
        action.data.id
      }&stock=${stockIdOrNew}`
    )
  }

  handleInitBookingLimitDatetime = () => {
    const {
      formBookingLimitDatetime,
      isOfferReadOnly,
      mergeForm,
      occurrence,
    } = this.props
    if (!get(occurrence, 'id') || formBookingLimitDatetime || isOfferReadOnly) {
      return
    }

    mergeForm('stock', {
      bookingLimitDatetime: moment(occurrence.beginningDatetime)
        .subtract(2, 'day')
        .toISOString(),
    })
  }

  handleInitEndDatetime = () => {
    const { formBeginningDatetime, mergeForm, occurrence } = this.props
    if (get(occurrence, 'id')) {
      return
    }
    mergeForm('occurrence', {
      endDatetime: moment(formBeginningDatetime)
        .add(1, 'hour')
        .toISOString(),
    })
  }

  handleInitPrice = () => {
    const { formPrice, mergeForm, stock } = this.props
    if (get(stock, 'id') || formPrice) {
      return
    }
    mergeForm('stock', { price: 0 })
  }

  handleNextDatetimes = () => {
    const {
      formBeginningDatetime,
      mergeForm,
      occurrence,
      occurrences,
    } = this.props
    // add automatically a default beginninDatetime and a endDatetime
    // one day after the previous occurrence
    if (get(occurrence, 'id')) {
      return
    }
    if (!formBeginningDatetime && get(occurrences, 'length')) {
      const beginningDatetime = moment(occurrences[0].beginningDatetime).add(
        1,
        'day'
      )
      mergeForm('occurrence', {
        beginningDatetime,
        endDatetime: moment(beginningDatetime).add(1, 'hour'),
      })
    }
  }

  handleOfferSuccessData = (state, action) => {
    const { history, offer } = this.props
    history.push(`/offres/${get(offer, 'id')}?gestion`)
  }

  handleResetForm = () => {
    const { isEditing, resetForm } = this.props
    if (!isEditing) {
      resetForm()
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
      formBeginningDatetime,
      isEditing,
      isEventOccurrenceReadOnly,
      isOfferReadOnly,
      offer,
      occurrence,
      occurrences,
      stock,
      tz,
    } = this.props

    const beginningDatetime =
      formBeginningDatetime || get(occurrence, 'beginningDatetime')

    return (
      <tr className="occurrence-form">
        <Form
          action={`/eventOccurrences/${get(occurrence, 'id', '')}`}
          handleSuccess={this.handleEventOccurrenceSuccessData}
          layout="input-only"
          name={`occurrence${get(occurrence, 'id', '')}`}
          patch={occurrence}
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
              highlightedDates={occurrences.map(o => o.beginningDatetime)}
              minDate="today"
              name="beginningDate"
              patchKey="beginningDatetime"
              readOnly={isEventOccurrenceReadOnly}
              required
              title="Date"
              type="date"
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
        <Form
          action={`/stocks/${get(stock, 'id', '')}`}
          handleSuccess={this.handleOfferSuccessData}
          layout="input-only"
          key={1}
          name={`stock${get(stock, 'id', '')}`}
          patch={stock}
          size="small"
          readOnly={isOfferReadOnly}
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
            <Field name="available" title="Places disponibles" type="number" />
          </td>
          {!isOfferReadOnly && (
            <Portal node={this.state.$submit}>
              <SubmitButton className="button is-primary is-small">
                Valider
              </SubmitButton>
            </Portal>
          )}
        </Form>
        <td>
          {isEditing ? (
            <NavLink
              className="button is-secondary is-small"
              to={`/offres/${get(offer, 'id')}?gestion`}>
              Annuler
            </NavLink>
          ) : (
            <button
              className="button is-small is-secondary"
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
              to={`/offres/${get(offer, 'id')}?gestion&date=${get(
                occurrence,
                'id'
              )}`}
              className="button is-small is-secondary">
              <span className="icon">
                <Icon svg="ico-pen-r" />
              </span>
            </NavLink>
          )}
        </td>
      </tr>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const search = searchSelector(state, ownProps.location.search)
      const { eventOccurrenceIdOrNew, stockIdOrNew } = search || {}

      const offer = offerSelector(state, ownProps.match.params.offerId)
      const { eventId, venueId } = offer || {}

      const occurrence = occurrenceSelector(
        state,
        ownProps.occurrence,
        ownProps.match.params.offerId,
        venueId
      )
      const occurrenceId = get(occurrence, 'id')

      const isEventOccurrenceReadOnly =
        !eventOccurrenceIdOrNew ||
        (eventOccurrenceIdOrNew === 'nouvelle' && occurrenceId) ||
        (eventOccurrenceIdOrNew !== 'nouvelle' &&
          occurrenceId !== eventOccurrenceIdOrNew) ||
        stockIdOrNew ||
        !ownProps.isFullyEditable

      const venue = venueSelector(state, venueId)

      const stock = stockSelector(
        state,
        get(ownProps, 'occurrence.id'),
        get(venue, 'managingOffererId')
      )
      const stockId = get(stock, 'id')

      const isOfferReadOnly =
        !occurrenceId ||
        !eventOccurrenceIdOrNew ||
        eventOccurrenceIdOrNew === 'nouvelle' ||
        eventOccurrenceIdOrNew !== occurrenceId ||
        !stockIdOrNew ||
        (stockIdOrNew === 'nouveau' && stockId) ||
        (stockIdOrNew !== 'nouveau' && stockId !== stockIdOrNew)

      const isEditing = !isEventOccurrenceReadOnly || !isOfferReadOnly

      return {
        event: eventSelector(state, eventId),
        eventId,
        eventOccurrenceIdOrNew,
        formBeginningDatetime: get(
          state,
          `form.occurrence${occurrenceId || ''}.beginningDatetime`
        ),
        formBookingLimitDatetime: get(
          state,
          `form.stock${stockId || ''}.bookingLimitDatetime`
        ),
        formEndDatetime: get(
          state,
          `form.occurrence${occurrenceId || ''}.endDatetime`
        ),
        formPrice: get(state, `form.stock${stockId || ''}.price`),
        isEditing,
        isEventOccurrenceReadOnly,
        isOfferReadOnly,
        occurrence,
        offer,
        occurrences: occurrencesSelector(state, venueId, eventId),
        stock,
        stockIdOrNew,
        tz: timezoneSelector(state, venueId),
        venue,
        venueId,
      }
    },
    { mergeForm, requestData, resetForm }
  )
)(OccurrenceForm)
