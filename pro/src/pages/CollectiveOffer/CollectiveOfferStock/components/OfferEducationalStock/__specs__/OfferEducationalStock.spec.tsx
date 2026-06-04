import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'

import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import { Mode } from '@/commons/core/OfferEducational/types'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
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
        priceDetail: 'Détail du prix',
      },
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByText('Indiquez le prix et la date de votre offre')
    ).toBeVisible()
    expect(screen.getByLabelText(/Date de début/)).toHaveValue('2022-02-10')
    expect(screen.getByLabelText(/Horaire/)).toHaveValue('01:00')
  })

  it.each`
    datetimeInput          | departementCode | expectedDateValue | expectedTimeValue
    ${'2022-02-10T00:00Z'} | ${'75'}         | ${'2022-02-10'}   | ${'01:00'}
    ${'2022-02-10T00:00Z'} | ${''}           | ${'2022-02-10'}   | ${'01:00'}
    ${'2022-02-10T00:00Z'} | ${'973'}        | ${'2022-02-09'}   | ${'21:00'}
  `(
    'when departement is $departement : should set a date value corresponding to the right timezone',
    ({
      datetimeInput,
      departementCode,
      expectedDateValue,
      expectedTimeValue,
    }) => {
      const testProps: OfferEducationalStockProps = {
        ...defaultProps,
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        ],
        initialStock: {
          startDatetime: datetimeInput,
          endDatetime: datetimeInput,
          bookingLimitDatetime: datetimeInput,
        },
        departementCode,
      }
      renderWithProviders(<OfferEducationalStock {...testProps} />)
      expect(screen.getByLabelText(/Date de début/)).toHaveValue(
        expectedDateValue
      )
      expect(screen.getAllByLabelText(/Date de fin/)[1]).toHaveValue(
        expectedDateValue
      )
      expect(screen.getByLabelText(/Date limite/)).toHaveValue(
        expectedDateValue
      )
      expect(screen.getByLabelText(/Horaire/)).toHaveValue(expectedTimeValue)
    }
  )

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
        priceDetail: 'Détail du prix',
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

  it('should send all data if the stock does not already exists', async () => {
    const user = userEvent.setup()

    const tomorrow = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      ],
      initialStock: {
        // no id given => stock doesn't exists
        startDatetime: format(tomorrow, FORMAT_ISO_DATE_ONLY),
        numberOfTickets: 10,
        price: 100,
        priceDetail: 'Détail du prix',
      },
      departementCode: '75',
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    const eventTime = '11:00',
      expectedEventTime = '09:00' // due to departementCode: '75'
    const today = format(new Date(), FORMAT_ISO_DATE_ONLY)

    await user.type(screen.getAllByLabelText(/Date de fin */)[1], tomorrow)
    await user.type(screen.getByLabelText(/Horaire */), eventTime)
    await user.type(screen.getByLabelText(/Date limite/), today)

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(testProps.onSubmit).toHaveBeenCalledExactlyOnceWith({
      startDatetime: `${tomorrow}T${expectedEventTime}:00Z`,
      endDatetime: `${tomorrow}T${expectedEventTime}:00Z`,
      bookingLimitDatetime: `${today}T21:59:59Z`,
      numberOfTickets: 10,
      price: 100,
      priceDetail: 'Détail du prix',
    })
  })

  it('should send only dirty data if the stock already exists', async () => {
    const user = userEvent.setup()

    const tomorrow = addDays(new Date(), 1).toISOString()
    const testProps: OfferEducationalStockProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
      initialStock: {
        id: 12, // this is how we know the stock exists.
        startDatetime: tomorrow,
        endDatetime: tomorrow,
        bookingLimitDatetime: tomorrow,
        numberOfTickets: 10,
        price: 100,
        priceDetail: 'Détail du prix',
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
      priceDetail: 'Nouveau contenu',
    })
  })
})
