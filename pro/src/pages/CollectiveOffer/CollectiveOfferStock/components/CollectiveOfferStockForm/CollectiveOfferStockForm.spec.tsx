import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { axe } from 'vitest-axe'

import {
  CollectiveAdditionalFeeType,
  CollectiveOfferAllowedAction,
} from '@/apiClient/v1'
import { Mode } from '@/commons/core/OfferEducational/types'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferStockForm,
  type CollectiveOfferStockFormProps,
} from './CollectiveOfferStockForm'

const defaultProps: CollectiveOfferStockFormProps = {
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

vi.mock(
  '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit',
  () => ({
    ScrollToFirstHookFormErrorAfterSubmit: () => null,
  })
)

describe('<CollectiveOfferStockForm />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <CollectiveOfferStockForm {...defaultProps} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render for offer with a stock in the past', () => {
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      initialStock: {
        startDatetime: '2022-02-10T00:00',
        endDatetime: '2022-02-10T00:00',
        bookingLimitDatetime: '2022-02-10T00:00',
        numberOfTickets: 10,
        numberOfTeachers: 2,
      },
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    expect(screen.getByText('Date de votre offre')).toBeVisible()
    expect(screen.getByLabelText(/Date de début/)).toHaveValue('2022-02-10')
    expect(screen.getByLabelText(/Date de fin/)).toHaveValue('2022-02-10')
    expect(screen.getByLabelText(/Horaire/)).toHaveValue('01:00')
    expect(screen.getByLabelText(/Date limite de réservation/)).toHaveValue(
      '2022-02-10'
    )
    expect(screen.getByLabelText(/Nombre d'élèves/)).toHaveValue(10)
    expect(screen.getByLabelText(/Nombre d'accompagnateurs/)).toHaveValue(2)
  })

  it('should display errors on empty fields then clear them when fields are filled', async () => {
    const user = userEvent.setup()
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      ],
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    const submitBtn = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await user.click(submitBtn)

    expect(screen.getByText('La date de début est obligatoire')).toBeVisible()
    expect(screen.getByText('La date de fin est obligatoire')).toBeVisible()
    expect(screen.getByText('L’horaire est obligatoire')).toBeVisible()
    expect(
      screen.getByText('La date limite de réservation est obligatoire')
    ).toBeVisible()
    expect(screen.getByText("Le nombre d'élèves est obligatoire")).toBeVisible()
    expect(
      screen.getByText("Le nombre d'accompagnateurs est obligatoire")
    ).toBeVisible()
    expect(
      screen.getByText('Le tarif de la prestation est obligatoire')
    ).toBeVisible()
    expect(testProps.onSubmit).not.toHaveBeenCalled()

    const userDateInput = format(addDays(new Date(), 5), FORMAT_ISO_DATE_ONLY)
    await user.type(screen.getByLabelText(/Date de début/), userDateInput)
    await user.type(screen.getByLabelText(/Horaire/), '00:00')
    await user.type(
      screen.getByLabelText(/Date limite de réservation/),
      userDateInput
    )
    await user.type(screen.getByLabelText(/Nombre d'élèves/), '10')
    await user.type(screen.getByLabelText(/Nombre d'accompagnateurs/), '2')
    await user.type(screen.getByLabelText(/Tarif de la prestation/), '100')

    expect(
      screen.queryByText('La date de début est obligatoire')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('La date de fin est obligatoire')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('L’horaire est obligatoire')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('La date limite de réservation est obligatoire')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText("Le nombre d'accompagnateurs est obligatoire")
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText("Le nombre d'élèves est obligatoire")
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Le tarif de la prestation est obligatoire')
    ).not.toBeInTheDocument()

    await user.click(submitBtn)
    expect(testProps.onSubmit).toHaveBeenCalledOnce()
  })

  it('should automatically update end date input when the user sets the start date after', async () => {
    const user = userEvent.setup()

    async function setStartDate(date: string) {
      const startDateInput = screen.getByLabelText(/Date de début/)
      await user.click(startDateInput)
      await user.clear(startDateInput)
      await waitFor(() => user.type(startDateInput, date))
    }

    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      initialStock: { startDatetime: new Date().toISOString() },
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    const today = format(new Date(), FORMAT_ISO_DATE_ONLY)
    const tomorrow = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    await setStartDate(tomorrow)
    const endDateInput = screen.getByLabelText(/Date de fin/)
    expect(endDateInput).toHaveValue(tomorrow)
    await setStartDate(today)
    expect(endDateInput).toHaveValue(tomorrow)
  })

  it('should disable all date fields when allowed actions does not have CAN_EDIT_DATES', () => {
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    expect(screen.getByLabelText(/Date de début/)).toBeDisabled()
    expect(screen.getByLabelText(/Date de fin/)).toBeDisabled()
    expect(screen.getByLabelText(/Horaire/)).toBeDisabled()
    expect(screen.getByLabelText(/Date limite de réservation/)).toBeDisabled()
  })

  it('should disable participants fields when allowed actions does not have CAN_EDIT_DISCOUNT', () => {
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
    }

    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    expect(screen.getByLabelText(/Nombre d'élèves/)).toBeDisabled()
    expect(screen.getByLabelText(/Nombre d'accompagnateurs/)).toBeDisabled()
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
      const testProps: CollectiveOfferStockFormProps = {
        ...defaultProps,
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
        initialStock: {
          startDatetime: datetimeInput,
          endDatetime: datetimeInput,
          bookingLimitDatetime: datetimeInput,
        },
        departementCode,
      }
      renderWithProviders(<CollectiveOfferStockForm {...testProps} />)
      expect(screen.getByLabelText(/Date de début/)).toHaveValue(
        expectedDateValue
      )
      expect(screen.getByLabelText(/Date de fin/)).toHaveValue(
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
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      initialStock: {
        startDatetime: tomorrow,
        endDatetime: tomorrow,
        bookingLimitDatetime: new Date().toISOString(),
        numberOfTickets: 10,
        numberOfTeachers: 10,
        servicePrice: 100,
        collectiveAdditionalFees: [],
      },
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)
    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    expect(submitButton).not.toBeDisabled()
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
        <CollectiveOfferStockForm {...defaultProps} mode={mode} />
      )

      expect(
        screen.queryByRole('link', { name: nonVisibleBtn })
      ).not.toBeInTheDocument()
      expect(screen.getByRole('link', { name: visibleBtn })).toBeVisible()
    }
  )

  it('should display saved information in the action bar', () => {
    renderWithProviders(<CollectiveOfferStockForm {...defaultProps} />)

    expect(screen.getByText('Brouillon enregistré')).toBeVisible()
    expect(screen.getByText('Enregistrer et continuer')).toBeVisible()
  })

  it('should send all data if the stock does not already exists', async () => {
    const user = userEvent.setup()

    const tomorrow = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      ],
      initialStock: {
        // no id given => stock doesn't exists
        startDatetime: format(tomorrow, FORMAT_ISO_DATE_ONLY),
        numberOfTickets: 10,
        numberOfTeachers: 1,
        servicePrice: 100,
        collectiveAdditionalFees: [],
      },
      departementCode: '75',
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    const eventTime = '11:00'
    const expectedEventTime = '09:00' // due to departementCode: '75';
    const today = format(new Date(), FORMAT_ISO_DATE_ONLY)

    await user.type(screen.getByLabelText(/Date de fin/), tomorrow)
    await user.type(screen.getByLabelText(/Horaire/), eventTime)
    await user.type(screen.getByLabelText(/Date limite/), today)

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(testProps.onSubmit).toHaveBeenCalledExactlyOnceWith({
      startDatetime: `${tomorrow}T${expectedEventTime}:00Z`,
      endDatetime: `${tomorrow}T${expectedEventTime}:00Z`,
      bookingLimitDatetime: `${today}T21:59:59Z`,
      numberOfTickets: 10,
      numberOfTeachers: 1,
      servicePrice: 100,
      price: 100,
      collectiveAdditionalFees: [],
    })
  })

  it('should send only dirty data if the stock already exists', async () => {
    const user = userEvent.setup()

    const tomorrow = addDays(new Date(), 1).toISOString()
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
      initialStock: {
        id: 12, // this is how we know the stock exists.
        startDatetime: tomorrow,
        endDatetime: tomorrow,
        bookingLimitDatetime: tomorrow,
        numberOfTickets: 10,
        numberOfTeachers: 1,
        servicePrice: 100,
        price: 100,
        collectiveAdditionalFees: [],
      },
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    const teachersInput = screen.getByLabelText(/Nombre d'accompagnateurs/)
    await user.clear(teachersInput)
    await user.type(teachersInput, '2')
    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(testProps.onSubmit).toHaveBeenCalledExactlyOnceWith({
      numberOfTeachers: 2,
    })
  })

  it('should save additional fees removal', async () => {
    const user = userEvent.setup()
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
      initialStock: {
        id: 12,
        startDatetime: addDays(new Date(), 1).toISOString(),
        endDatetime: addDays(new Date(), 1).toISOString(),
        bookingLimitDatetime: new Date().toISOString(),
        numberOfTickets: 10,
        numberOfTeachers: 1,
        servicePrice: 100,
        price: 130,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.MEAL, label: null, amount: 10 },
          { type: CollectiveAdditionalFeeType.TRAVEL, label: null, amount: 20 },
        ],
      },
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    const trashButtons = screen.getAllByRole('button', {
      name: 'Supprimer ce champ',
    })
    await user.click(trashButtons[0])

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(testProps.onSubmit).toHaveBeenCalledExactlyOnceWith(
      expect.objectContaining({
        servicePrice: 100,
        collectiveAdditionalFees: [
          expect.objectContaining({ type: 'TRAVEL', amount: 20 }),
        ],
        price: 120,
      })
    )
  })

  it('should compute and display the price when servicePrice or additionalFees change', async () => {
    const user = userEvent.setup()
    const tomorrow = addDays(new Date(), 1).toISOString()
    const testProps: CollectiveOfferStockFormProps = {
      ...defaultProps,
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      ],
      initialStock: {
        id: 12,
        startDatetime: tomorrow,
        endDatetime: tomorrow,
        bookingLimitDatetime: tomorrow,
        numberOfTickets: 10,
        numberOfTeachers: 1,
        servicePrice: 100,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.ACCOMMODATION,
            label: null,
            amount: 10,
          },
          { type: CollectiveAdditionalFeeType.TRAVEL, label: null, amount: 20 },
        ],
      },
    }
    renderWithProviders(<CollectiveOfferStockForm {...testProps} />)

    const priceHeading = screen.getByRole('heading', {
      name: /Prix total de votre offre/,
    })
    expect(priceHeading).toHaveTextContent(/130/)

    const servicePriceInput = screen.getByLabelText(
      /Tarif de la prestation \(en €\)/
    )
    await user.clear(servicePriceInput)
    await user.type(servicePriceInput, '150')

    expect(priceHeading).toHaveTextContent(/180/)

    const feeAmountInputs = screen.getAllByLabelText(/Prix \(en €\)/)
    expect(feeAmountInputs[0]).toHaveValue(10)
    expect(feeAmountInputs[1]).toHaveValue(20)
    await user.clear(feeAmountInputs[0])
    await waitFor(() => user.type(feeAmountInputs[0], '15'))
    expect(feeAmountInputs[0]).toHaveValue(15)

    expect(priceHeading).toHaveTextContent(/185/)

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(testProps.onSubmit).toHaveBeenCalledExactlyOnceWith({
      servicePrice: 150,
      collectiveAdditionalFees: [
        {
          type: CollectiveAdditionalFeeType.ACCOMMODATION,
          label: null,
          amount: 15,
        },
        { type: CollectiveAdditionalFeeType.TRAVEL, label: null, amount: 20 },
      ],
      price: 185,
    })
  })
})
