import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'
import {
  getCanSubmit,
  bindTimeFieldWithDateField,
} from 'react-final-form-utils'
import { requestData } from 'redux-saga-data'

import EditAndDeleteControl from './EditAndDeleteControl'
import EventFields from './EventFields'
import fillEndDatimeWhenUpdatingBeginningDatetime from './fillEndDatimeWhenUpdatingBeginningDatetime'
import ProductFields from './ProductFields'
import SubmitAndCancelControlContainer from './SubmitAndCancelControl/SubmitAndCancelControlContainer'
import adaptBookingLimitDateTimeGivenBeginningDateTime from './decorators/adaptBookingLimitDateTimeGivenBeginningDateTime'
import { errorKeyToFrenchKey } from './utils'

export class StockItem extends Component {
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
    const { query, stockPatch } = this.props
    const { id: stockId } = stockPatch
    const nextState = { isRequestPending: false }
    this.setState(nextState, () => {
      query.changeToReadOnly(null, { id: stockId, key: 'stock' })
      formResolver()
    })
  }

  onFormSubmit = formValues => {
    const { dispatch, handleSetErrors, query, stockPatch } = this.props
    const { id: stockId } = stockPatch
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
      isEvent,
      offer,
      query,
      showInfo,
      stock,
      stockPatch,
      stocks,
      timezone,
      venue,
    } = this.props
    const { isRequestPending, tbodyElement } = this.state
    const { id: stockId } = stockPatch
    const { readOnly } = query.context({ id: stockId, key: 'stock' })

    let decorators = [
      adaptBookingLimitDateTimeGivenBeginningDateTime({
        isEvent,
      }),
    ]

    if (isEvent) {
      decorators = decorators.concat([
        fillEndDatimeWhenUpdatingBeginningDatetime({
          triggerDateName: 'beginningDatetime',
          targetDateName: 'endDatetime',
          targetTimeName: 'endTime',
        }),
        bindTimeFieldWithDateField({
          dateName: 'beginningDatetime',
          timeName: 'beginningTime',
          timezone,
        }),
        bindTimeFieldWithDateField({
          dateName: 'endDatetime',
          timeName: 'endTime',
          timezone,
        }),
      ])
    }

    return (
      <tbody
        ref={_element => {
          this.tbodyElement = _element
        }}>
        <Form
          decorators={decorators}
          initialValues={stockPatch}
          onSubmit={this.onFormSubmit}
          render={formProps => {
            const { form, values, handleSubmit } = formProps
            const { beginningDatetime } = values
            const canSubmit = getCanSubmit(
              Object.assign({}, formProps, { pristine: false })
            )

            return (
              <tr className="stock-item">
                {isEvent && (
                  <EventFields
                    dispatch={dispatch}
                    readOnly={readOnly}
                    stockPatch={stockPatch}
                    stocks={stocks}
                    timezone={timezone}
                    values={values}
                  />
                )}
                <ProductFields
                  beginningDatetime={beginningDatetime}
                  closeInfo={closeInfo}
                  dispatch={dispatch}
                  hasIban={hasIban}
                  isEvent={isEvent}
                  readOnly={readOnly}
                  offer={offer}
                  showInfo={showInfo}
                  stock={stock}
                  timezone={timezone}
                  venue={venue}
                />
                {readOnly ? (
                  <EditAndDeleteControl
                    dispatch={dispatch}
                    formInitialValues={stockPatch}
                    history={history}
                    isEvent={isEvent}
                    offer={offer}
                    stock={stock}
                    tbody={tbodyElement}
                  />
                ) : (
                  <SubmitAndCancelControlContainer
                    canSubmit={canSubmit}
                    form={form}
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

StockItem.defaultProps = {
  closeInfo: PropTypes.func.isRequired,
  formBeginningDatetime: null,
  formBookingLimitDatetime: null,
  formEndDatetime: null,
  offer: null,
  showInfo: PropTypes.func.isRequired,
  stocks: null,
  timezone: null,
}

StockItem.propTypes = {
  closeInfo: PropTypes.func.isRequired,
  dispatch: PropTypes.func.isRequired,
  hasIban: PropTypes.bool.isRequired,
  history: PropTypes.shape().isRequired,
  isEvent: PropTypes.bool.isRequired,
  offer: PropTypes.shape(),
  query: PropTypes.shape().isRequired,
  stockPatch: PropTypes.shape().isRequired,
  stocks: PropTypes.arrayOf(PropTypes.object),
  showInfo: PropTypes.func.isRequired,
  timezone: PropTypes.string,
  venue: PropTypes.shape(),
}

export default StockItem
