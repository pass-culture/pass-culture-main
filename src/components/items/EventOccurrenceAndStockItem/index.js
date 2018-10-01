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

import EventOccurenceDateTime from './EventOccurenceDateTime'
import mapStateToProps from './mapStateToProps'

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
          endDatetime: moment(formBeginningDatetime)
            .add(1, 'day')
            .toISOString(),
        })
      )
    }
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
      const beginningDatetime = moment(eventOccurrences[0].beginningDatetime)
        .add(1, 'day')
        .toISOString()
      const endDatetime = moment(eventOccurrences[0].endDatetime)
        .add(1, 'day')
        .toISOString()
      dispatch(
        mergeForm(`eventOccurrence${get(eventOccurrencePatch, 'id', '')}`, {
          beginningDatetime,
          endDatetime,
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
            <EventOccurenceDateTime
              eventOccurrencePatch={eventOccurrencePatch}
              isEventOccurrenceReadOnly={isEventOccurrenceReadOnly}
              beginningDatetime={beginningDatetime}
              eventOccurrences={eventOccurrences}
              tz={tz}
              submit={this.state.$submit}
              history={this.props.history}
              offer={offer}
              stockPatch={stockPatch}
            />
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
                maxDate={isStockOnly ? undefined : beginningDatetime}
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
              toutes les réservations associées. {!isStockOnly && <br />}
              Êtes-vous sûr•e de vouloir continuer&nbsp;?
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
  connect(mapStateToProps)
)(EventOccurrenceAndStockItem)
