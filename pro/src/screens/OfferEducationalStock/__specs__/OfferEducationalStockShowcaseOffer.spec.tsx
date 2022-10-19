import '@testing-library/jest-dom'

import userEvent from '@testing-library/user-event'

import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
} from 'core/OfferEducational'
import { configureTestStore } from 'store/testUtils'

import {
  collectiveOfferTemplateFactory,
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

    expect(showCaseOptionRadioButton).toBeInTheDocument()

    expect(showCaseOptionRadioButton?.checked).toBe(false)
    await userEvent.click(showCaseOptionRadioButton as HTMLInputElement)
    expect(showCaseOptionRadioButton?.checked).toBe(true)

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
      offer: collectiveOfferTemplateFactory({}),
      initialValues: {
        ...DEFAULT_EAC_STOCK_FORM_VALUES,
        priceDetail: 'Détail du prix',
        educationalOfferType: EducationalOfferType.SHOWCASE,
      },
      mode: Mode.EDITION,
    }
    renderOfferEducationalStock(testProps)

    const showCaseOptionRadioButton = queryShowcaseOfferRadio()

    expect(showCaseOptionRadioButton).toBeInTheDocument()
    expect(showCaseOptionRadioButton?.checked).toBe(true)

    const priceDetailsTextArea = queryPriceDetailsTextarea()
    expect(priceDetailsTextArea).toHaveValue('Détail du prix')

    const classicOptionRadioButton = queryClassicOfferRadio()
    await userEvent.click(classicOptionRadioButton as HTMLInputElement)

    expect(showCaseOptionRadioButton?.checked).toBe(false)
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

  it('should not show radio buttons if offer has a stock and is not showcase', () => {
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer: offerFactory({}),
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

  describe('radio buttons', () => {
    it('should display radio button when creating offer', async () => {
      renderOfferEducationalStock(props)
      const showCaseOptionRadioButton = queryShowcaseOfferRadio()
      const classicOptionRadioButton = queryClassicOfferRadio()
      expect(showCaseOptionRadioButton).toBeInTheDocument()
      expect(classicOptionRadioButton).toBeInTheDocument()
    })

    it('should display radio button when editing offer if duplication FF is off and offer is showcase', async () => {
      renderOfferEducationalStock({
        ...props,
        mode: Mode.EDITION,
        offer: collectiveOfferTemplateFactory({}),
        initialValues: {
          ...DEFAULT_EAC_STOCK_FORM_VALUES,
          educationalOfferType: EducationalOfferType.SHOWCASE,
        },
      })
      const showCaseOptionRadioButton = queryShowcaseOfferRadio()
      const classicOptionRadioButton = queryClassicOfferRadio()
      expect(showCaseOptionRadioButton).toBeInTheDocument()
      expect(classicOptionRadioButton).toBeInTheDocument()
    })

    it('should not display radio button when editing offer when offer is not showcase', async () => {
      renderOfferEducationalStock({
        ...props,
        mode: Mode.EDITION,
      })

      const showCaseOptionRadioButton = queryShowcaseOfferRadio()
      const classicOptionRadioButton = queryClassicOfferRadio()
      expect(showCaseOptionRadioButton).not.toBeInTheDocument()
      expect(classicOptionRadioButton).not.toBeInTheDocument()
    })

    it('should not display radio button when editing offer if duplication FF is on and offer is showcase', async () => {
      renderOfferEducationalStock(
        {
          ...props,
          mode: Mode.EDITION,
          offer: collectiveOfferTemplateFactory({}),
          initialValues: {
            ...DEFAULT_EAC_STOCK_FORM_VALUES,
            educationalOfferType: EducationalOfferType.SHOWCASE,
          },
        },
        configureTestStore({
          features: {
            list: [
              {
                isActive: true,
                nameKey: 'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE',
              },
            ],
          },
        })
      )

      const showCaseOptionRadioButton = queryShowcaseOfferRadio()
      const classicOptionRadioButton = queryClassicOfferRadio()
      expect(showCaseOptionRadioButton).not.toBeInTheDocument()
      expect(classicOptionRadioButton).not.toBeInTheDocument()
    })
  })

  it('should nos display radio button when duplication offer', async () => {
    renderOfferEducationalStock(
      {
        ...props,
        isCreatingFromTemplate: true,
        mode: Mode.EDITION,
        initialValues: {
          ...DEFAULT_EAC_STOCK_FORM_VALUES,
          educationalOfferType: EducationalOfferType.SHOWCASE,
        },
      },
      configureTestStore({
        features: {
          list: [
            {
              isActive: true,
              nameKey: 'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE',
            },
          ],
        },
      })
    )

    const showCaseOptionRadioButton = queryShowcaseOfferRadio()
    const classicOptionRadioButton = queryClassicOfferRadio()
    expect(showCaseOptionRadioButton).not.toBeInTheDocument()
    expect(classicOptionRadioButton).not.toBeInTheDocument()
  })
})
