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
import occurrenceSelector from '../../selectors/occurrence'
import occurrencesSelector from '../../selectors/occurrences'
import offerSelector from '../../selectors/offer'
import searchSelector from '../../selectors/search'
import stockSelector from '../../selectors/stock'
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
    const { dispatch, occurrence } = this.props
    dispatch(requestData('DELETE', `eventOccurrences/${occurrence.id}`))
  }

  handleCrossingEndDatetime = () => {
    const { dispatch, formBeginningDatetime, formEndDatetime } = this.props
    if (formEndDatetime < formBeginningDatetime) {
      dispatch(
        mergeForm('occurrence', {
          endDatetime: moment(formEndDatetime)
            .add(1, 'day')
            .toISOString(),
        })
      )
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
      dispatch,
      formBookingLimitDatetime,
      isStockReadOnly,
      occurrence,
    } = this.props
    if (!get(occurrence, 'id') || formBookingLimitDatetime || isStockReadOnly) {
      return
    }
    dispatch(
      mergeForm('stock', {
        bookingLimitDatetime: moment(occurrence.beginningDatetime)
          .subtract(2, 'day')
          .toISOString(),
      })
    )
  }

  handleInitEndDatetime = () => {
    const { dispatch, formBeginningDatetime, occurrence } = this.props
    if (get(occurrence, 'id')) {
      return
    }
    dispatch(
      mergeForm('occurrence', {
        endDatetime: moment(formBeginningDatetime)
          .add(1, 'hour')
          .toISOString(),
      })
    )
  }

  handleInitPrice = () => {
    const { dispatch, formPrice, stock } = this.props
    if (get(stock, 'id') || formPrice) {
      return
    }
    dispatch(mergeForm('stock', { price: 0 }))
  }

  handleNextDatetimes = () => {
    const {
      dispatch,
      formBeginningDatetime,
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
      dispatch(
        mergeForm('occurrence', {
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
      formBeginningDatetime,
      isEditing,
      isEventOccurrenceReadOnly,
      isStockOnly,
      isStockReadOnly,
      offer,
      occurrence,
      occurrences,
      stock,
      tz,
    } = this.props
    const { isDeleting } = this.state

    const beginningDatetime =
      formBeginningDatetime || get(occurrence, 'beginningDatetime')

    console.log('isStockOnly', isStockOnly)

    return (
      <Fragment>
        <tr
          className={classnames('event-occurrences-and-stocks-item', {
            'with-confirm': isDeleting,
          })}>
          <Form
            action={`/eventOccurrences/${get(occurrence, 'id', '')}`}
            handleSuccess={this.handleEventOccurrenceSuccessData}
            layout="input-only"
            name={`occurrence${get(occurrence, 'id', '')}`}
            patch={occurrence}
            readOnly={isEventOccurrenceReadOnly}
            size="small"
            Tag={null}>
            {!isStockOnly && (
              <Fragment>
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
              </Fragment>
            )}
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
        {isDeleting && (
          <tr>
            <td className="is-size-7" colSpan="6">
              En confirmant l'annulation de cette date, vous supprimerez aussi
              toutes les réservations associées. <br />
              Êtes-vous sûrs de vouloir continuer&nbsp;?
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

    const isStockReadOnly =
      !occurrenceId ||
      !eventOccurrenceIdOrNew ||
      eventOccurrenceIdOrNew === 'nouvelle' ||
      eventOccurrenceIdOrNew !== occurrenceId ||
      !stockIdOrNew ||
      (stockIdOrNew === 'nouveau' && stockId) ||
      (stockIdOrNew !== 'nouveau' && stockId !== stockIdOrNew)

    const isEditing = !isEventOccurrenceReadOnly || !isStockReadOnly

    console.log(
      'isStockReadOnly',
      isStockReadOnly,
      'isEventOccurrenceReadOnly',
      isEventOccurrenceReadOnly
    )

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
      isStockReadOnly,
      occurrence,
      offer,
      occurrences: occurrencesSelector(state, venueId, eventId),
      stock,
      stockIdOrNew,
      tz: timezoneSelector(state, venueId),
      venue,
      venueId,
    }
  })
)(EventOccurrenceAndStockItem)
