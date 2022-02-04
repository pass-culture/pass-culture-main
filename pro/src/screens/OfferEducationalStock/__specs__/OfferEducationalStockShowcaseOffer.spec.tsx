import '@testing-library/jest-dom'
import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  defaultProps,
  renderOfferEducationalStock,
  elements,
} from '../__tests-utils__'
import { IOfferEducationalStockProps } from '../OfferEducationalStock'

const {
  queryShowcaseOfferRadio,
  queryBeginningDateInput,
  queryBeginningTimeInput,
  queryNumberOfPlacesInput,
  queryPriceInput,
  queryBookingLimitDatetimeInput,
  queryPriceDetailsTextarea,
} = elements

describe('screens | OfferEducationalStock : showcase offer', () => {
  let props: IOfferEducationalStockProps
  beforeEach(() => {
    props = {
      ...defaultProps,
    }
  })

  it('should hide stock form when user select showcase option', async () => {
    renderOfferEducationalStock(props)
    const showCaseOptionRadioButton = queryShowcaseOfferRadio()

    await waitFor(() => expect(showCaseOptionRadioButton).toBeInTheDocument())

    expect(showCaseOptionRadioButton?.checked).toBe(false)
    userEvent.click(showCaseOptionRadioButton as HTMLInputElement)
    await waitFor(() =>
      expect(expect(showCaseOptionRadioButton?.checked).toBe(true))
    )

    const beginningDateInput = queryBeginningDateInput()
    const beginningTimeInput = queryBeginningTimeInput()
    const numberOfPlacesInput = queryNumberOfPlacesInput()
    const priceInput = queryPriceInput()
    const bookingLimitDatetimeInput = queryBookingLimitDatetimeInput()
    const priceDetailsTextArea = queryPriceDetailsTextarea()

    expect(beginningDateInput).not.toBeInTheDocument()
    expect(beginningTimeInput).not.toBeInTheDocument()
    expect(numberOfPlacesInput).not.toBeInTheDocument()
    expect(priceInput).not.toBeInTheDocument()
    expect(bookingLimitDatetimeInput).not.toBeInTheDocument()
    expect(priceDetailsTextArea).toBeInTheDocument()
  })
})
