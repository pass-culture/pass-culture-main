import get from 'lodash.get'
import { mergeForm, resetForm } from 'pass-culture-shared'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import DateTimeForm from './DateTimeForm'
import PriceQuantityForm from './PriceQuantityForm'
import Actions from './Actions'
import mapStateToProps from './mapStateToProps'

class EventOccurrenceAndStockItem extends Component {
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

  handleResetForm = () => {
    const { dispatch, isEditing } = this.props
    if (!isEditing) {
      dispatch(resetForm())
    }
  }

  getFormStep() {
    if (this.props.isEventOccurrenceReadOnly === true) {
      return 0
    }

    if (this.props.isEventOccurrenceReadOnly === false) {
      return 1
    }

    return 2
  }

  componentWillMount() {
    this.handleResetForm()
  }

  componentDidMount() {
    this.handleNextDatetimes()
    this.handleInitBookingLimitDatetime()
    this.handleInitPrice()
  }

  componentDidUpdate(prevProps, prevState) {
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
      closeInfo,
      eventOccurrencePatch,
      eventOccurrences,
      formBeginningDatetime,
      formPrice,
      hasIban,
      isEditing,
      isEventOccurrenceReadOnly,
      isStockOnly,
      isStockReadOnly,
      offer,
      showInfo,
      stockPatch,
      tz,
    } = this.props

    const beginningDatetime =
      formBeginningDatetime || get(eventOccurrencePatch, 'beginningDatetime')

    return (
      <tbody ref={DOMNode => (this.tbody = DOMNode)}>
        <tr className="event-occurrence-and-stock-item">
          {!isStockOnly && (
            <DateTimeForm
              beginningDatetime={beginningDatetime}
              eventOccurrencePatch={eventOccurrencePatch}
              eventOccurrences={eventOccurrences}
              history={this.props.history}
              isEventOccurrenceReadOnly={isEventOccurrenceReadOnly}
              offer={offer}
              stockPatch={stockPatch}
              tz={tz}
            />
          )}

          {this.getFormStep() !== 1 && (
            <PriceQuantityForm
              beginningDatetime={beginningDatetime}
              closeInfo={closeInfo}
              formPrice={formPrice}
              hasIban={hasIban}
              history={this.props.history}
              isStockOnly={isStockOnly}
              isStockReadOnly={isStockReadOnly}
              offer={offer}
              showInfo={showInfo}
              stockPatch={stockPatch}
            />
          )}

          {!isEditing && (
            <Actions
              eventOccurrencePatch={eventOccurrencePatch}
              isEditing={isEditing}
              isStockOnly={isStockOnly}
              offer={offer}
              stockPatch={stockPatch}
              tbody={this.tbody}
            />
          )}
        </tr>
      </tbody>
    )
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(EventOccurrenceAndStockItem)
