import '@testing-library/jest-dom'

import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
} from 'core/OfferEducational'

import {
  defaultProps,
  elements,
  offerFactory,
  renderOfferEducationalStock,
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
  queryClassicOfferRadio,
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

  it('should prefill form with default values when user is editing stock and offer is showcase', async () => {
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer: offerFactory({ isShowcase: true }),
      initialValues: {
        ...DEFAULT_EAC_STOCK_FORM_VALUES,
        priceDetail: 'Détail du prix',
        educationalOfferType: EducationalOfferType.SHOWCASE,
      },
      mode: Mode.EDITION,
    }
    renderOfferEducationalStock(testProps)

    const showCaseOptionRadioButton = queryShowcaseOfferRadio()

    await waitFor(() => expect(showCaseOptionRadioButton).toBeInTheDocument())
    expect(showCaseOptionRadioButton?.checked).toBe(true)

    const priceDetailsTextArea = queryPriceDetailsTextarea()
    expect(priceDetailsTextArea).toHaveValue('Détail du prix')

    const classicOptionRadioButton = queryClassicOfferRadio()
    userEvent.click(classicOptionRadioButton as HTMLInputElement)

    await waitFor(() => expect(showCaseOptionRadioButton?.checked).toBe(false))
    expect(classicOptionRadioButton?.checked).toBe(true)

    const beginningDateInput = queryBeginningDateInput()
    const beginningTimeInput = queryBeginningTimeInput()
    const numberOfPlacesInput = queryNumberOfPlacesInput()
    const priceInput = queryPriceInput()
    const bookingLimitDatetimeInput = queryBookingLimitDatetimeInput()
    expect(beginningDateInput).toBeInTheDocument()
    expect(beginningDateInput?.value).toBe('')
    expect(beginningTimeInput).toBeInTheDocument()
    expect(beginningTimeInput?.value).toBe('')
    expect(numberOfPlacesInput).toBeInTheDocument()
    expect(numberOfPlacesInput?.value).toBe('')
    expect(priceInput).toBeInTheDocument()
    expect(priceInput?.value).toBe('')
    expect(bookingLimitDatetimeInput).toBeInTheDocument()
    expect(bookingLimitDatetimeInput?.value).toBe('')
  })

  it('should not show radio buttons if offer has a stock and is not showcase', async () => {
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer: offerFactory({ isShowcase: false }),
      initialValues: {
        eventDate: new Date('2022-02-10T00:00:00.000Z'),
        eventTime: new Date('2022-02-10T00:00:00.000Z'),
        bookingLimitDatetime: new Date('2022-02-10'),
        numberOfPlaces: 10,
        totalPrice: 100,
        priceDetail: 'Détail du prix',
        educationalOfferType: EducationalOfferType.CLASSIC,
      },
      mode: Mode.EDITION,
    }
    renderOfferEducationalStock(testProps)

    const showCaseOptionRadioButton = queryShowcaseOfferRadio()
    const classicOptionRadioButton = queryClassicOfferRadio()

    expect(showCaseOptionRadioButton).not.toBeInTheDocument()
    expect(classicOptionRadioButton).not.toBeInTheDocument()
  })
})
