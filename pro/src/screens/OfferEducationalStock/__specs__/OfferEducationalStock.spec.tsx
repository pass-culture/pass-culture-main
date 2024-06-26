import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, addMinutes, format, subDays } from 'date-fns'
import React from 'react'
import * as router from 'react-router-dom'

import { CollectiveBookingStatus } from 'apiClient/v1'
import { DEFAULT_EAC_STOCK_FORM_VALUES } from 'core/OfferEducational/constants'
import { Mode, EducationalOfferType } from 'core/OfferEducational/types'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferCollectiveStockFactory,
} from 'utils/collectiveApiFactories'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PRICE_DETAIL_PLACEHOLDER } from '../constants/labels'
import {
  OfferEducationalStock,
  OfferEducationalStockProps,
} from '../OfferEducationalStock'

const defaultProps: OfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: getCollectiveOfferFactory({}),
  onSubmit: vi.fn(),
  mode: Mode.CREATION,
}

const tomorrow = addDays(new Date(), 1)
const initialValuesNotEmpty = {
  ...DEFAULT_EAC_STOCK_FORM_VALUES,
  startDatetime: format(tomorrow, FORMAT_ISO_DATE_ONLY),
  endDatetime: format(tomorrow, FORMAT_ISO_DATE_ONLY),
  eventTime: format(addMinutes(tomorrow, 15), FORMAT_HH_mm),
  bookingLimitDatetime: '2023-03-30',
  numberOfPlaces: 10,
  totalPrice: 100,
  priceDetail: 'Détail du prix',
}

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: vi.fn(),
}))

describe('OfferEducationalStock', () => {
  const mockNavigate = vi.fn()
  beforeEach(() => {
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })
  it('should render for offer with a stock', () => {
    const offer = getCollectiveOfferFactory()
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        startDatetime: '2022-02-10',
        endDatetime: '2022-02-10',
        eventTime: '00:00',
        bookingLimitDatetime: '2022-02-10',
        numberOfPlaces: 10,
        totalPrice: 100,
        priceDetail: 'Détail du prix',
        educationalOfferType: EducationalOfferType.CLASSIC,
      },
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    screen.getByText('Dates et prix')
  })

  it('should render for offer imported with a public api', () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: true })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByText('Offre importée automatiquement')
    ).toBeInTheDocument()
  })

  it.each([
    getCollectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
    }),
    getCollectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.USED,
      collectiveStock: getCollectiveOfferCollectiveStockFactory({
        startDatetime: subDays(new Date(), 1).toDateString(),
      }),
    }),
  ])(
    'should not disable description, price and places when offer is $lastBookingStatus since less than 2 days',
    (offer) => {
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        mode: Mode.READ_ONLY,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const descriptionInput = screen.getByPlaceholderText(
        PRICE_DETAIL_PLACEHOLDER
      )
      const priceInput = screen.getByLabelText('Prix total TTC *')
      const placeInput = screen.getByLabelText('Nombre de participants *')

      expect(descriptionInput).not.toBeDisabled()
      expect(priceInput).not.toBeDisabled()
      expect(placeInput).not.toBeDisabled()
    }
  )

  it.each([
    getCollectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.REIMBURSED,
    }),
    getCollectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.USED,
      collectiveStock: getCollectiveOfferCollectiveStockFactory({
        startDatetime: subDays(new Date(), 3).toDateString(),
      }),
    }),
  ])(
    'should disable save button, description, price and places when offer is reimbursed or is used since more than 2 days',
    (offer) => {
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        mode: Mode.READ_ONLY,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const descriptionInput = screen.getByPlaceholderText(
        PRICE_DETAIL_PLACEHOLDER
      )
      const priceInput = screen.getByLabelText('Prix total TTC *')
      const placeInput = screen.getByLabelText('Nombre de participants *')
      const saveButton = screen.getByText('Enregistrer les modifications')

      expect(descriptionInput).toBeDisabled()
      expect(priceInput).toBeDisabled()
      expect(placeInput).toBeDisabled()
      expect(saveButton).toBeDisabled()
    }
  )

  it('should call submit callback when clicking next step with valid form data', async () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: false })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: initialValuesNotEmpty,
      mode: Mode.CREATION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)
    const submitButton = screen.getByRole('button', { name: 'Étape suivante' })
    await userEvent.click(submitButton)

    expect(testProps.onSubmit).toHaveBeenCalled()
  })

  it('should display error message when price and participants are too high', async () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: false })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        ...initialValuesNotEmpty,
        totalPrice: 60001,
        numberOfPlaces: 3001,
      },
      mode: Mode.CREATION,
    }

    renderWithProviders(<OfferEducationalStock {...testProps} />)
    const submitButton = screen.getByRole('button', { name: 'Étape suivante' })
    await userEvent.click(submitButton)

    expect(
      screen.getByText('Le nombre de participants ne doit pas dépasser 3000')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Le prix ne doit pas dépasser 60 000€')
    ).toBeInTheDocument()
  })

  it('should display error message when selected event time is less than current time', async () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: false })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        ...initialValuesNotEmpty,
        startDatetime: String(new Date()),
        eventTime: '02:00',
      },
      mode: Mode.CREATION,
    }

    renderWithProviders(<OfferEducationalStock {...testProps} />)
    const submitButton = screen.getByRole('button', { name: 'Étape suivante' })
    await userEvent.click(submitButton)

    expect(
      screen.getByText("L'heure doit être postérieure à l'heure actuelle")
    ).toBeInTheDocument()
  })

  it('should have a cancel button instead of the previous step button when editing the offer', () => {
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      mode: Mode.EDITION,
    }

    renderWithProviders(<OfferEducationalStock {...testProps} />)
    expect(
      screen.queryByRole('button', { name: /Étape suivante/ })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Annuler et quitter' })
    ).not.toBeInTheDocument()
  })
})

it('should automatically update bookingLimitDatetime when the user edits the start date', async () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    mode: Mode.CREATION,
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  const userDateInput = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
  const dateInput = screen.getByLabelText('Date de début *')
  await userEvent.click(dateInput)
  await userEvent.clear(dateInput)
  await waitFor(() => userEvent.type(dateInput, userDateInput))
  const bookingLimitDatetimeInput = screen.getByLabelText(
    'Date limite de réservation *'
  )
  expect(bookingLimitDatetimeInput).toHaveValue(userDateInput)
})

it('should disable booking limit datetime when form access is read only', () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    mode: Mode.READ_ONLY,
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  const bookingLimitDatetimeInput = screen.getByLabelText(
    'Date limite de réservation *'
  )

  expect(bookingLimitDatetimeInput).toBeDisabled()
})
