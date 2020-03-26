import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit } from 'react-final-form-utils'

import EditAndDeleteControl from './sub-components/EditAndDeleteControl/EditAndDeleteControl'
import EventFields from './sub-components/fields/EventFields/EventFields'
import adaptBookingLimitDatetimeGivenBeginningDatetime from './decorators/adaptBookingLimitDatetimeGivenBeginningDatetime'
import bindTimeFieldWithDateField from './decorators/bindTimeFieldWithDateField'
import SubmitAndCancelControlContainer from './sub-components/SubmitAndCancelControl/SubmitAndCancelControlContainer'
import { errorKeyToFrenchKey } from './utils/utils'
import ProductFieldsContainer from './sub-components/fields/ProductFields/ProductFieldsContainer'
import Offer from '../../ValueObjects/Offer'

class StockItem extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isRequestPending: false,
      tbodyElement: null,
    }
  }

  componentDidMount() {
    this.updateTBodyElement()
  }

  updateTBodyElement() {
    this.setState({ tbodyElement: this.tbodyElement })
  }

  createTBodyRef = () => element => {
    this.tbodyElement = element
  }

  handleRequestFail = (state, action) => {
    const { handleSetErrors } = this.props
    const {
      payload: { errors },
    } = action
    this.setState({ isRequestPending: false })
    const frenchErrors = Object.keys(errors)
      .filter(errorKeyToFrenchKey)
      .reduce(
        (result, errorKey) =>
          Object.assign({ [errorKeyToFrenchKey(errorKey)]: errors[errorKey] }, result),
        null
      )
    handleSetErrors(frenchErrors)
  }

  handleRequestSuccess = () => {
    const { query, stockPatch } = this.props
    const { id: stockId } = stockPatch

    this.setState({ isRequestPending: false })
    query.changeToReadOnly(null, { id: stockId, key: 'stock' })
  }

  handleOnFormSubmit = formValues => {
    const { handleSetErrors, stockPatch, isEvent, updateStockInformations } = this.props
    const { id: stockId } = stockPatch
    this.setState({ isRequestPending: true })

    handleSetErrors()
    const body = Object.assign({}, formValues)
    if (body.price === '') {
      body.price = 0
    }
    if (body.available === '') {
      body.available = null
    }
    if (isEvent && body.bookingLimitDatetime === '') {
      body.bookingLimitDatetime = body.beginningDatetime
    }

    return updateStockInformations(stockId, body, this.handleRequestSuccess, this.handleRequestFail)
  }

  renderForm = formProps => {
    const {
      closeInfo,
      deleteStock,
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
      handleSetErrors,
    } = this.props

    const { isRequestPending, tbodyElement } = this.state
    const { id: stockId } = stockPatch
    const { readOnly } = query.context({ id: stockId, key: 'stock' })
    const userIsNotUpdatingStock = readOnly
    const { form, values, handleSubmit } = formProps
    const { beginningDatetime } = values
    const canSubmit = getCanSubmit(Object.assign({}, formProps, { pristine: false }))

    return (
      <tr className="stock-item">
        {isEvent && (
          <EventFields
            beginningDatetime={beginningDatetime}
            readOnly={userIsNotUpdatingStock || offer.hasBeenProvidedByAllocine}
            stockPatch={stockPatch}
            stocks={stocks}
            timezone={timezone}
            values={values}
          />
        )}
        <ProductFieldsContainer
          beginningDatetime={beginningDatetime}
          closeInfo={closeInfo}
          formProps={formProps}
          hasIban={hasIban}
          isEvent={isEvent}
          offer={offer}
          readOnly={userIsNotUpdatingStock}
          showInfo={showInfo}
          stock={stock}
          timezone={timezone}
          venue={venue}
        />
        {userIsNotUpdatingStock ? (
          <EditAndDeleteControl
            deleteStock={deleteStock}
            formInitialValues={stockPatch}
            handleSetErrors={handleSetErrors}
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
  }

  render() {
    const { isEvent, stockPatch, timezone } = this.props
    let decorators = [
      adaptBookingLimitDatetimeGivenBeginningDatetime({
        isEvent,
        timezone,
      }),
    ]

    if (isEvent) {
      decorators = decorators.concat([
        bindTimeFieldWithDateField({
          dateName: 'beginningDatetime',
          timeName: 'beginningTime',
          timezone,
        }),
      ])
    }

    return (
      <tbody ref={this.createTBodyRef()}>
        <Form
          decorators={decorators}
          initialValues={stockPatch}
          onSubmit={this.handleOnFormSubmit}
          render={this.renderForm}
        />
      </tbody>
    )
  }
}

StockItem.defaultProps = {
  offer: null,
  stocks: null,
  timezone: null,
  venue: {},
}

StockItem.propTypes = {
  closeInfo: PropTypes.func.isRequired,
  deleteStock: PropTypes.func.isRequired,
  handleSetErrors: PropTypes.func.isRequired,
  hasIban: PropTypes.bool.isRequired,
  history: PropTypes.shape().isRequired,
  isEvent: PropTypes.bool.isRequired,
  offer: PropTypes.instanceOf(Offer),
  query: PropTypes.shape().isRequired,
  showInfo: PropTypes.func.isRequired,
  stockPatch: PropTypes.shape().isRequired,
  stocks: PropTypes.arrayOf(PropTypes.shape()),
  timezone: PropTypes.string,
  updateStockInformations: PropTypes.func.isRequired,
  venue: PropTypes.shape(),
}

export default StockItem
