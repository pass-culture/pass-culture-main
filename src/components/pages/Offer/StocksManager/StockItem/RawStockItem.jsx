import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'
import {
  getCanSubmit,
  selectBoundDatesFromTriggerDateNameAndTargetDateNameAndTimezoneDecorator,
  selectTimeDecoratorFromTimeNameAndDateNameAndTimezoneDecorator,
} from 'react-final-form-utils'
import { requestData } from 'redux-saga-data'

import EditAndDeleteControl from './EditAndDeleteControl'
import EventFields from './EventFields'
import ProductFields from './ProductFields'
import SubmitAndCancelControl from './SubmitAndCancelControl'
import { errorKeyToFrenchKey } from './utils'

export class RawStockItem extends Component {
  constructor() {
    super()
    this.state = {
      isRequestPending: false,
      tbodyElement: null,
    }
  }

  componentDidMount() {
    this.setState({ tbodyElement: this.tbodyElement })
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
    const { query, formInitialValues } = this.props
    const { id: stockId } = formInitialValues
    const nextState = { isRequestPending: false }
    this.setState(nextState, () => {
      query.changeToReadOnly(null, { id: stockId, key: 'stock' })
      formResolver()
    })
  }

  onFormSubmit = formValues => {
    const { dispatch, handleSetErrors, query, formInitialValues } = this.props
    const { id: stockId } = formInitialValues
    const context = query.context({ id: stockId, key: 'stock' })
    const { method } = context
    const apiPath = `/stocks/${stockId || ''}`
    this.setState({ isRequestPending: true })

    handleSetErrors()

    const body = Object.assign({}, formValues)
    if (body.price === '') {
      body.price = 0
    }
    if (body.available === '') {
      body.available = null
    }

    const formSubmitPromise = new Promise(resolve => {
      dispatch(
        requestData({
          apiPath,
          body,
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
      stock,
      formInitialValues,
      stocks,
      tz,
    } = this.props
    const { isRequestPending, tbodyElement } = this.state
    const { id: stockId } = formInitialValues
    const { readOnly } = query.context({ id: stockId, key: 'stock' })

    return (
      <tbody
        ref={_element => {
          this.tbodyElement = _element
        }}>
        <Form
          decorators={
            isEventStock && [
              selectBoundDatesFromTriggerDateNameAndTargetDateNameAndTimezoneDecorator(
                'beginningDatetime',
                'endDatetime',
                tz
              ),
              selectTimeDecoratorFromTimeNameAndDateNameAndTimezoneDecorator(
                'beginningTime',
                'beginningDatetime',
                tz
              ),
              selectTimeDecoratorFromTimeNameAndDateNameAndTimezoneDecorator(
                'endTime',
                'endDatetime',
                tz
              ),
            ]
          }
          initialValues={formInitialValues}
          onSubmit={this.onFormSubmit}
          render={formProps => {
            const { values, handleSubmit } = formProps
            const { beginningDatetime } = values
            const canSubmit = getCanSubmit(
              Object.assign({}, formProps, { pristine: false })
            )
            return (
              <tr className="stock-item">
                {isEventStock && (
                  <EventFields
                    dispatch={dispatch}
                    readOnly={readOnly}
                    formInitialValues={formInitialValues}
                    stocks={stocks}
                    tz={tz}
                    values={values}
                  />
                )}
                <ProductFields
                  beginningDatetime={beginningDatetime}
                  closeInfo={closeInfo}
                  dispatch={dispatch}
                  hasIban={hasIban}
                  isEventStock={isEventStock}
                  readOnly={readOnly}
                  offer={offer}
                  showInfo={showInfo}
                  stock={stock}
                />
                {readOnly ? (
                  <EditAndDeleteControl
                    dispatch={dispatch}
                    history={history}
                    isEventStock={isEventStock}
                    offer={offer}
                    stock={stock}
                    tbody={tbodyElement}
                    stockPatch={stockPatch}
                  />
                ) : (
                  <SubmitAndCancelControl
                    canSubmit={canSubmit}
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
  formInitialValues: PropTypes.object.isRequired,
  stocks: PropTypes.arrayOf(PropTypes.object),
  showInfo: PropTypes.func.isRequired,
}

export default RawStockItem
