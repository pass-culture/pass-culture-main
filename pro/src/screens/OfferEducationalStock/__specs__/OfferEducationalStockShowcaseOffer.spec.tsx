import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'
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
  offerFactory,
  renderOfferEducationalStock,
} from '../__tests-utils__'
import {
  BOOKING_LIMIT_DATETIME_LABEL,
  DETAILS_PRICE_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'
import { IOfferEducationalStockProps } from '../OfferEducationalStock'

describe('screens | OfferEducationalStock : showcase offer', () => {
  let props: IOfferEducationalStockProps
  beforeEach(() => {
    props = {
      ...defaultProps,
    }
  })

  it('should hide stock form when user select showcase option', async () => {
    renderOfferEducationalStock(props)
    const showCaseOptionRadioButton = screen.getByLabelText(
      'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
    ) as HTMLInputElement

    expect(showCaseOptionRadioButton).toBeInTheDocument()

    expect(showCaseOptionRadioButton?.checked).toBe(false)
    await userEvent.click(showCaseOptionRadioButton as HTMLInputElement)
    expect(showCaseOptionRadioButton?.checked).toBe(true)

    const beginningDateInput = screen.queryByLabelText(EVENT_DATE_LABEL)
    const beginningTimeInput = screen.queryByLabelText(EVENT_TIME_LABEL)
    const numberOfPlacesInput = screen.queryByLabelText(NUMBER_OF_PLACES_LABEL)
    const priceInput = screen.queryByLabelText(TOTAL_PRICE_LABEL)
    const bookingLimitDatetimeInput = screen.queryByLabelText(
      BOOKING_LIMIT_DATETIME_LABEL
    )
    const priceDetailsTextArea = screen.queryByLabelText(DETAILS_PRICE_LABEL, {
      exact: false,
    })

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

    const showCaseOptionRadioButton = screen.getByLabelText(
      'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
    ) as HTMLInputElement

    expect(showCaseOptionRadioButton).toBeInTheDocument()
    expect(showCaseOptionRadioButton?.checked).toBe(true)

    const priceDetailsTextArea = screen.queryByLabelText(DETAILS_PRICE_LABEL, {
      exact: false,
    })
    expect(priceDetailsTextArea).toHaveValue('Détail du prix')

    const classicOptionRadioButton = screen.getByLabelText(
      'Je connais la date et le prix de mon offre'
    ) as HTMLInputElement
    await userEvent.click(classicOptionRadioButton)

    expect(showCaseOptionRadioButton?.checked).toBe(false)
    expect(classicOptionRadioButton?.checked).toBe(true)

    const beginningDateInput = screen.getByLabelText(
      EVENT_DATE_LABEL
    ) as HTMLInputElement
    const beginningTimeInput = screen.getByLabelText(
      EVENT_TIME_LABEL
    ) as HTMLInputElement
    const numberOfPlacesInput = screen.getByLabelText(
      NUMBER_OF_PLACES_LABEL
    ) as HTMLInputElement
    const priceInput = screen.getByLabelText(
      TOTAL_PRICE_LABEL
    ) as HTMLInputElement
    const bookingLimitDatetimeInput = screen.getByLabelText(
      BOOKING_LIMIT_DATETIME_LABEL
    ) as HTMLInputElement

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

    const showCaseOptionRadioButton = screen.queryByLabelText(
      'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
    )
    const classicOptionRadioButton = screen.queryByLabelText(
      'Je connais la date et le prix de mon offre'
    )

    expect(showCaseOptionRadioButton).not.toBeInTheDocument()
    expect(classicOptionRadioButton).not.toBeInTheDocument()
  })

  describe('radio buttons', () => {
    it('should display radio button when creating offer', async () => {
      renderOfferEducationalStock(props)
      const showCaseOptionRadioButton = screen.queryByLabelText(
        'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
      )
      const classicOptionRadioButton = screen.queryByLabelText(
        'Je connais la date et le prix de mon offre'
      )
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
      const showCaseOptionRadioButton = screen.getByLabelText(
        'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
      )
      const classicOptionRadioButton = screen.getByLabelText(
        'Je connais la date et le prix de mon offre'
      )
      expect(showCaseOptionRadioButton).toBeInTheDocument()
      expect(classicOptionRadioButton).toBeInTheDocument()
    })

    it('should not display radio button when editing offer when offer is not showcase', async () => {
      renderOfferEducationalStock({
        ...props,
        mode: Mode.EDITION,
      })

      const showCaseOptionRadioButton = screen.queryByLabelText(
        'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
      )
      const classicOptionRadioButton = screen.queryByLabelText(
        'Je connais la date et le prix de mon offre'
      )
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

      const showCaseOptionRadioButton = screen.queryByLabelText(
        'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
      )
      const classicOptionRadioButton = screen.queryByLabelText(
        'Je connais la date et le prix de mon offre'
      )
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

    const showCaseOptionRadioButton = screen.queryByLabelText(
      'Je préfère être contacté par un enseignant avant de définir la date et le prix de l’offre'
    )
    const classicOptionRadioButton = screen.queryByLabelText(
      'Je connais la date et le prix de mon offre'
    )
    expect(showCaseOptionRadioButton).not.toBeInTheDocument()
    expect(classicOptionRadioButton).not.toBeInTheDocument()
  })
})
