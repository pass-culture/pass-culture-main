import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import { Mode } from '@/commons/core/OfferEducational/types'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferEducationalStock,
  type OfferEducationalStockProps,
} from '../OfferEducationalStock'

const defaultProps: OfferEducationalStockProps = {
  initialStock: {},
  departementCode: '75',
  allowedActions: [],
  onSubmit: vi.fn(),
  mode: Mode.CREATION,
}

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

afterEach(() => {
  vi.clearAllMocks()
})

describe('OfferEducationalStock', () => {
  it('should render for offer with a stock in the past', () => {
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      initialStock: {
        startDatetime: '2022-02-10T00:00',
        endDatetime: '2022-02-10T00:00',
        bookingLimitDatetime: '2022-02-10T00:00',
        numberOfTickets: 10,
        price: 100,
        educationalPriceDetail: 'Détail du prix',
      },
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByText('Indiquez le prix et la date de votre offre')
    ).toBeVisible()
  })

  it('should call submit callback when clicking next step with valid form data and edit action is allowed', async () => {
    const user = userEvent.setup()

    const tomorrow = addDays(new Date(), 1).toISOString()
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      initialStock: {
        startDatetime: tomorrow,
        endDatetime: tomorrow,
        bookingLimitDatetime: new Date().toISOString(),
        numberOfTickets: 10,
        price: 100,
        educationalPriceDetail: 'Détail du prix',
      },
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)
    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await user.click(submitButton)

    expect(testProps.onSubmit).toHaveBeenCalled()
  })

  it.each`
    mode             | visibleBtn              | nonVisibleBtn
    ${Mode.CREATION} | ${'Retour'}             | ${'Annuler et quitter'}
    ${Mode.EDITION}  | ${'Annuler et quitter'} | ${'Retour'}
  `(
    'should have a $visibleBtn button instead of the $nonVisibleBtn button on $mode mode',
    ({ mode, visibleBtn, nonVisibleBtn }) => {
      renderWithProviders(
        <OfferEducationalStock {...defaultProps} mode={mode} />
      )

      expect(
        screen.queryByRole('link', { name: nonVisibleBtn })
      ).not.toBeInTheDocument()
      expect(screen.getByRole('link', { name: visibleBtn })).toBeVisible()
    }
  )

  it('should disable booking limit date when allowed actions does not have CAN_EDIT_DATES', () => {
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
    }

    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(screen.getByLabelText('Date limite de réservation *')).toBeDisabled()
  })

  it('should display saved information in the action bar', () => {
    renderWithProviders(<OfferEducationalStock {...defaultProps} />)

    expect(screen.getByText('Brouillon enregistré')).toBeVisible()
    expect(screen.getByText('Enregistrer et continuer')).toBeVisible()
  })

  it('should not disable description, price and places when action CAN_EDIT_DISCOUNT is allowed', () => {
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
    }

    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByRole('textbox', {
        name: /Informations sur le prix(?: |\u00A0)\*/,
      })
    ).not.toBeDisabled()
  })

  it('should disable description, price and places when allowed action CAN_EDIT_DISCOUNT doesnt exist', () => {
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
    }

    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByRole('textbox', {
        name: /Informations sur le prix(?: |\u00A0)\*/,
      })
    ).toBeDisabled()
  })

  it('should send only dirty data if the stock already exists', async () => {
    const user = userEvent.setup()

    const tomorrow = addDays(new Date(), 1).toISOString()
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
      initialStock: {
        startDatetime: tomorrow,
        endDatetime: tomorrow,
        bookingLimitDatetime: tomorrow,
        numberOfTickets: 10,
        price: 100,
        educationalPriceDetail: 'Détail du prix',
      },
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    const priceDetailsTextarea = screen.getByRole('textbox', {
      name: /Informations sur le prix(?: |\u00A0)\*/,
    })

    expect(priceDetailsTextarea).toBeVisible()

    await user.clear(priceDetailsTextarea)
    await user.type(priceDetailsTextarea, 'Nouveau contenu')

    expect(priceDetailsTextarea).toHaveValue('Nouveau contenu')

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(testProps.onSubmit).toHaveBeenCalledExactlyOnceWith({
      educationalPriceDetail: 'Nouveau contenu',
    })
  })
})
