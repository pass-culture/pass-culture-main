import classnames from 'classnames'
import get from 'lodash.get'
import { mergeForm, requestData, resetForm } from 'pass-culture-shared'
import moment from 'moment'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import DateTimeForm from './DateTimeForm'
import CommonForm from './CommonForm'
import Actions from './Actions'
import Delete from './Delete'
import mapStateToProps from './mapStateToProps'

class EventOccurrenceAndStockItem extends Component {
  constructor(props) {
    super(props)
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
            <DateTimeForm
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

          <CommonForm
            stockPatch={stockPatch}
            isStockReadOnly={isStockReadOnly}
            beginningDatetime={beginningDatetime}
            history={this.props.history}
            submit={this.state.$submit}
            offer={offer}
          />

          <Actions
            isEditing={isEditing}
            offer={offer}
            isStockOnly={isStockOnly}
            stockPatch={stockPatch}
            eventOccurrencePatch={eventOccurrencePatch}
            onRef={element => (this.$submit = element)}
            onDeleteClick={this.onDeleteClick}
          />
        </tr>

        {isDeleting && (
          <Delete
            eventOccurrencePatch={eventOccurrencePatch}
            isStockOnly={isStockOnly}
            stockPatch={stockPatch}
            onCancelDeleteClick={this.onCancelDeleteClick}
            onConfirmDeleteClick={this.onConfirmDeleteClick}
          />
        )}
      </Fragment>
    )
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(EventOccurrenceAndStockItem)
