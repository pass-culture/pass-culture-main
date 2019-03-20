import { Form, resetForm } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

import EditAndDeleteControl from './EditAndDeleteControl'
import EventFields from './EventFields'
import EventOrThingFields from './EventOrThingFields'
import SubmitAndCancelControl from './SubmitAndCancelControl'

export class RawStockItem extends Component {
  componentDidUpdate(prevProps, prevState) {
    const { isReadOnly } = this.props
    if (!prevProps.isReadOnly && isReadOnly) {
      this.handleResetForm()
    }
  }

  componentWillMount() {
    this.handleResetForm()
  }

  handleResetForm = () => {
    const { dispatch, isReadOnly } = this.props
    if (isReadOnly) {
      dispatch(resetForm())
    }
  }

  handleSuccess = (state, action) => {
    const { history, offer } = this.props
    const { id: offerId } = offer
    history.push(`/offres/${offerId}?gestion`)
  }

  render() {
    const {
      closeInfo,
      dispatch,
      formBeginningDatetime,
      formBookingLimitDatetime,
      formEndDatetime,
      formPrice,
      hasIban,
      history,
      isEventStock,
      isReadOnly,
      offer,
      showInfo,
      stockFormKey,
      stockPatch,
      stocks,
      tz,
    } = this.props
    let { beginningDatetime } = stockPatch || {}
    beginningDatetime = formBeginningDatetime || beginningDatetime

    const name = `stock${stockFormKey}`
    let action = ''
    let stockId
    if (stockPatch && stockPatch.id) {
      stockId = stockPatch.id
      action = `/stocks/${stockId}`
    } else if (stockPatch && stockPatch.id) {
      stockId = stockPatch.id
      action = `/stocks/${stockId}`
    } else if (!isReadOnly) {
      action = '/stocks'
      stockId = null
    }

    return (
      <tbody ref={DOMNode => (this.tbody = DOMNode)}>
        <Form
          action={action}
          BlockComponent={null}
          className="stock-item"
          handleSuccess={this.handleSuccess}
          layout="input-only"
          name={name}
          patch={stockPatch}
          size="small"
          readOnly={isReadOnly}
          Tag="tr">
          {isEventStock && (
            <EventFields
              beginningDatetime={beginningDatetime}
              dispatch={dispatch}
              formBeginningDatetime={formBeginningDatetime}
              formBookingLimitDatetime={formBookingLimitDatetime}
              formEndDatetime={formEndDatetime}
              isReadOnly={isReadOnly}
              stockFormKey={stockFormKey}
              stockPatch={stockPatch}
              stocks={stocks}
              tz={tz}
            />
          )}
          <EventOrThingFields
            beginningDatetime={beginningDatetime}
            closeInfo={closeInfo}
            dispatch={dispatch}
            formPrice={formPrice}
            hasIban={hasIban}
            isEventStock={isEventStock}
            isReadOnly={isReadOnly}
            offer={offer}
            showInfo={showInfo}
            stockFormKey={stockFormKey}
            stockPatch={stockPatch}
          />
          {isReadOnly ? (
            <EditAndDeleteControl
              dispatch={dispatch}
              history={history}
              isEventStock={isEventStock}
              offer={offer}
              stockPatch={stockPatch}
              tbody={this.tbody}
            />
          ) : (
            <SubmitAndCancelControl offer={offer} />
          )}
        </Form>
      </tbody>
    )
  }
}

RawStockItem.defaultProps = {
  closeInfo: PropTypes.func.isRequired,
  formBeginningDatetime: null,
  formBookingLimitDatetime: null,
  formEndDatetime: null,
  isReadOnly: null,
  offer: null,
  showInfo: PropTypes.func.isRequired,
  stocks: null,
}

RawStockItem.propTypes = {
  closeInfo: PropTypes.func.isRequired,
  formBeginningDatetime: PropTypes.string,
  formBookingLimitDatetime: PropTypes.string,
  formEndDatetime: PropTypes.string,
  hasIban: PropTypes.bool.isRequired,
  history: PropTypes.object.isRequired,
  isEventStock: PropTypes.bool.isRequired,
  isReadOnly: PropTypes.bool,
  offer: PropTypes.object,
  stocks: PropTypes.arrayOf(PropTypes.object),
  showInfo: PropTypes.func.isRequired,
}

export default RawStockItem
