import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, addMinutes, format, subDays } from 'date-fns'
import React from 'react'
import * as router from 'react-router-dom'

import { CollectiveBookingStatus } from 'apiClient/v1'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
} from 'core/OfferEducational'
import {
  collectiveOfferFactory,
  getCollectiveOfferCollectiveStockFactory,
} from 'utils/collectiveApiFactories'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalStock, {
  OfferEducationalStockProps,
} from '../OfferEducationalStock'

const defaultProps: OfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: collectiveOfferFactory({}),
  onSubmit: vi.fn(),
  mode: Mode.CREATION,
}

const tomorrow = addDays(new Date(), 1)
const initialValuesNotEmpty = {
  ...DEFAULT_EAC_STOCK_FORM_VALUES,
  eventDate: format(tomorrow, FORMAT_ISO_DATE_ONLY),
  eventTime: format(addMinutes(tomorrow, 15), FORMAT_HH_mm),
  bookingLimitDatetime: '2023-03-30',
  numberOfPlaces: 10,
  totalPrice: 100,
  priceDetail: 'Détail du prix',
}

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useNavigate: vi.fn(),
}))

describe('OfferEducationalStock', () => {
  const mockNavigate = vi.fn()
  beforeEach(() => {
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })
  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory()
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        eventDate: '2022-02-10',
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

    screen.getByText('Date et prix')
  })

  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })
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
    collectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
    }),
    collectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.USED,
      collectiveStock: getCollectiveOfferCollectiveStockFactory({
        beginningDatetime: subDays(new Date(), 1).toDateString(),
      }),
    }),
  ])(
    'should not disable description, price and places when offer is confirmed or used since less than 2 days',
    (offer) => {
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        mode: Mode.READ_ONLY,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const descriptionInput = screen.getByPlaceholderText(
        'Détaillez ici des informations complémentaires.'
      )
      const priceInput = screen.getByLabelText('Prix global TTC *')
      const placeInput = screen.getByLabelText('Nombre de participants *')

      expect(descriptionInput).not.toBeDisabled()
      expect(priceInput).not.toBeDisabled()
      expect(placeInput).not.toBeDisabled()
    }
  )

  it.each([
    collectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.REIMBURSED,
    }),
    collectiveOfferFactory({
      lastBookingStatus: CollectiveBookingStatus.USED,
      collectiveStock: getCollectiveOfferCollectiveStockFactory({
        beginningDatetime: subDays(new Date(), 3).toDateString(),
      }),
    }),
  ])(
    'should disable description, price and places when offer is reimbursed or is used since more than 2 days',
    (offer) => {
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        offer,
        mode: Mode.READ_ONLY,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)

      const descriptionInput = screen.getByPlaceholderText(
        'Détaillez ici des informations complémentaires.'
      )
      const priceInput = screen.getByLabelText('Prix global TTC *')
      const placeInput = screen.getByLabelText('Nombre de participants *')

      expect(descriptionInput).toBeDisabled()
      expect(priceInput).toBeDisabled()
      expect(placeInput).toBeDisabled()
    }
  )

  it('should call submit callback when clicking next step with valid form data', async () => {
    const offer = collectiveOfferFactory({ isPublicApi: false })
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
    const offer = collectiveOfferFactory({ isPublicApi: false })
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

  it('should display error message when price and participants are too high', async () => {
    const offer = collectiveOfferFactory({ isPublicApi: false })
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        ...initialValuesNotEmpty,
        eventDate: String(new Date()),
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
})
