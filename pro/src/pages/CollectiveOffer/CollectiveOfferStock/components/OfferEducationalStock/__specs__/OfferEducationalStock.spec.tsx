import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, addMinutes, format } from 'date-fns'
import * as router from 'react-router'

import { CollectiveOfferAllowedAction } from 'apiClient/v1'
import { DEFAULT_EAC_STOCK_FORM_VALUES } from 'commons/core/OfferEducational/constants'
import { Mode } from 'commons/core/OfferEducational/types'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { DETAILS_PRICE_LABEL } from '../constants/labels'
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
  bookingLimitDatetime: format(new Date(), FORMAT_ISO_DATE_ONLY),
  numberOfPlaces: 10,
  totalPrice: 100,
  priceDetail: 'Détail du prix',
}

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
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
      },
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    screen.getByText('Indiquez le prix et la date de votre offre')
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

  it('should call submit callback when clicking next step with valid form data and edit action is allowed', async () => {
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      }),
      initialValues: initialValuesNotEmpty,
      mode: Mode.CREATION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)
    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await userEvent.click(submitButton)

    expect(testProps.onSubmit).toHaveBeenCalled()
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

it('should disable booking limit datetime when form access is read only', () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    mode: Mode.READ_ONLY,
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  const bookingLimitDatetimeInput = screen.getByLabelText(
    'Date limite de réservation'
  )

  expect(bookingLimitDatetimeInput).toBeDisabled()
})

it('should display saved information in the action bar', () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    mode: Mode.CREATION,
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()

  expect(screen.getByText('Enregistrer et continuer')).toBeInTheDocument()
})

it('should not disable start datetime, end datetime and event time inputs when date edition is allowed', () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    offer: getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
    }),
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  const startDatetimeInput = screen.getByLabelText('Date de début')
  const endDatetimeInput = screen.getAllByLabelText(/Date de fin/)[1]
  const eventTimeInput = screen.getByLabelText('Horaire')

  expect(startDatetimeInput).not.toBeDisabled()
  expect(endDatetimeInput).not.toBeDisabled()
  expect(eventTimeInput).not.toBeDisabled()
})

it('should not disable description, price and places when action CAN_EDIT_DISCOUNT is allowed', () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    mode: Mode.EDITION,
    offer: getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
    }),
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  const descriptionInput = screen.getByRole('textbox', {
    name: `${DETAILS_PRICE_LABEL}`,
  })
  const priceInput = screen.getByLabelText('Prix total TTC')
  const placeInput = screen.getByLabelText('Nombre de participants')

  expect(descriptionInput).not.toBeDisabled()
  expect(priceInput).not.toBeDisabled()
  expect(placeInput).not.toBeDisabled()
})

it('should disable description, price and places when allowed action CAN_EDIT_DISCOUNT doesnt exist', () => {
  const testProps: OfferEducationalStockProps = {
    ...defaultProps,
    mode: Mode.EDITION,
    offer: getCollectiveOfferFactory({
      allowedActions: [],
    }),
  }

  renderWithProviders(<OfferEducationalStock {...testProps} />)

  const descriptionInput = screen.getByRole('textbox', {
    name: `${DETAILS_PRICE_LABEL}`,
  })
  const priceInput = screen.getByLabelText('Prix total TTC')
  const placeInput = screen.getByLabelText('Nombre de participants')

  expect(descriptionInput).toBeDisabled()
  expect(priceInput).toBeDisabled()
  expect(placeInput).toBeDisabled()
})
