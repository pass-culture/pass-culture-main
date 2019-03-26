import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'
import { requestData } from 'redux-saga-data'

import EditAndDeleteControl from './EditAndDeleteControl'
import EventFields from './EventFields'
import EventOrThingFields from './EventOrThingFields'
import SubmitAndCancelControl from './SubmitAndCancelControl'
import { errorKeyToFrenchKey } from './utils'
import { selectTimeDecoratorFromTimeNameAndDateNameAndTz } from 'components/layout/form'

export class RawStockItem extends Component {
  constructor() {
    super()
    this.state = {
      isRequestPending: false,
    }
  }

  handleRequestFail = formResolver => (state, action) => {
    const { handleSetErrors } = this.props
    const {
      payload: { errors },
    } = action
    const nextState = { isRequestPending: false }
    const frenchErrors = Object.keys(errors)
      .filter(errorKeyToFrenchKey)
      .reduce(
        (result, errorKey) =>
          Object.assign(
            { [errorKeyToFrenchKey(errorKey)]: errors[errorKey] },
            result
          ),
        null
      )
    this.setState(nextState, () => handleSetErrors(frenchErrors))
  }

  handleRequestSuccess = formResolver => () => {
    const { query, stockPatch } = this.props
    const { id: stockId } = stockPatch
    const nextState = { isRequestPending: false }
    this.setState(nextState, () => {
      query.changeToReadOnlyUrl('stock', stockId)
      formResolver()
    })
  }

  onFormSubmit = formValues => {
    const { dispatch, query, stockPatch } = this.props
    const { id: stockId } = stockPatch
    const context = query.context('stock', stockId)
    const { method } = context
    const apiPath = `/stocks/${stockId || ''}`
    this.setState({ isRequestPending: true })

    const formSubmitPromise = new Promise(resolve => {
      dispatch(
        requestData({
          apiPath,
          body: { ...formValues },
          handleFail: this.handleRequestFail(resolve),
          handleSuccess: this.handleRequestSuccess(resolve),
          method,
        })
      )
    })
    return formSubmitPromise
  }

  render() {
    const {
      closeInfo,
      dispatch,
      hasIban,
      history,
      isEventStock,
      offer,
      query,
      showInfo,
      stockPatch,
      stocks,
      tz,
    } = this.props
    const { isRequestPending } = this.state
    const { id: stockId } = stockPatch
    const { readOnly } = query.context('stock', stockId)

    return (
      <tbody ref={DOMNode => (this.tbody = DOMNode)}>
        <Form
          decorators={[
            selectTimeDecoratorFromTimeNameAndDateNameAndTz(
              'beginningTime',
              'beginningDatetime',
              tz
            ),
            selectTimeDecoratorFromTimeNameAndDateNameAndTz(
              'endTime',
              'endDatetime',
              tz
            ),
          ]}
          initialValues={stockPatch}
          onSubmit={this.onFormSubmit}
          render={({ form, values, handleSubmit }) => {
            const { beginningDatetime } = values
            return (
              <tr className="stock-item">
                {isEventStock && (
                  <EventFields
                    dispatch={dispatch}
                    readOnly={readOnly}
                    stockPatch={stockPatch}
                    stocks={stocks}
                    tz={tz}
                    values={values}
                  />
                )}
                <EventOrThingFields
                  beginningDatetime={beginningDatetime}
                  closeInfo={closeInfo}
                  dispatch={dispatch}
                  hasIban={hasIban}
                  isEventStock={isEventStock}
                  readOnly={readOnly}
                  offer={offer}
                  showInfo={showInfo}
                  stockPatch={stockPatch}
                />
                {readOnly ? (
                  <EditAndDeleteControl
                    dispatch={dispatch}
                    history={history}
                    isEventStock={isEventStock}
                    offer={offer}
                    stockPatch={stockPatch}
                    tbody={this.tbody}
                  />
                ) : (
                  <SubmitAndCancelControl
                    handleSubmit={handleSubmit}
                    isRequestPending={isRequestPending}
                    stockId={stockId}
                  />
                )}
              </tr>
            )
          }}
        />
      </tbody>
    )
  }
}

RawStockItem.defaultProps = {
  closeInfo: PropTypes.func.isRequired,
  formBeginningDatetime: null,
  formBookingLimitDatetime: null,
  formEndDatetime: null,
  offer: null,
  showInfo: PropTypes.func.isRequired,
  stocks: null,
}

RawStockItem.propTypes = {
  closeInfo: PropTypes.func.isRequired,
  dispatch: PropTypes.func.isRequired,
  hasIban: PropTypes.bool.isRequired,
  history: PropTypes.object.isRequired,
  isEventStock: PropTypes.bool.isRequired,
  offer: PropTypes.object,
  query: PropTypes.object.isRequired,
  stockPatch: PropTypes.object.isRequired,
  stocks: PropTypes.arrayOf(PropTypes.object),
  showInfo: PropTypes.func.isRequired,
}

export default RawStockItem
