import { yupResolver } from '@hookform/resolvers/yup'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import {
  Mode,
  type OfferEducationalStockFormValues,
} from '@/commons/core/OfferEducational/types'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { Button } from '@/design-system/Button/Button'

import { generateValidationSchema } from '../../validationSchema'
import { FormStock } from '../FormStock'

function renderFormStock({
  initialValues,
  allowedActions,
  onSubmit = vi.fn(),
  options,
}: {
  initialValues: OfferEducationalStockFormValues
  allowedActions: CollectiveOfferAllowedAction[]
  onSubmit: () => void
  options?: RenderWithProvidersOptions
}) {
  function FormStockWrapper() {
    const form = useForm({
      defaultValues: initialValues,
      resolver: yupResolver<OfferEducationalStockFormValues, unknown, unknown>(
        generateValidationSchema(allowedActions, initialValues.totalPrice)
      ),
      mode: 'onTouched',
    })

    const props = {
      canEditDiscount: allowedActions.includes(
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
      ),
      canEditDates: allowedActions.includes(
        CollectiveOfferAllowedAction.CAN_EDIT_DATES
      ),
      mode:
        allowedActions.length === 0
          ? Mode.READ_ONLY
          : allowedActions.includes(
                CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
              )
            ? Mode.CREATION
            : Mode.EDITION,
    }

    return (
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormStock {...props} />
          <Button type="submit" label="Enregistrer" />
        </form>
      </FormProvider>
    )
  }

  return renderWithProviders(<FormStockWrapper />, options)
}

describe('FormStock', () => {
  let initialValues: OfferEducationalStockFormValues
  const onSubmit = vi.fn()
  let allowedActions: CollectiveOfferAllowedAction[]

  beforeEach(() => {
    initialValues = {
      startDate: '',
      endDate: '',
      eventTime: '',
      numberOfPlaces: null,
      totalPrice: null,
      bookingLimitDate: '',
      priceDetail: '',
    }

    allowedActions = [
      CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
    ]
  })

  it('should display an error when the field is empty', async () => {
    renderFormStock({
      initialValues,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      onSubmit,
    })

    const saveButton = screen.getByRole('button', { name: 'Enregistrer' })

    await userEvent.click(saveButton)

    expect(
      screen.getByText('La date de début est obligatoire')
    ).toBeInTheDocument()
    expect(
      screen.getByText('La date de fin est obligatoire')
    ).toBeInTheDocument()
    expect(screen.getByText('L’horaire est obligatoire')).toBeInTheDocument()
    expect(
      screen.getByText('Le nombre de participants est obligatoire')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Le prix total TTC est obligatoire')
    ).toBeInTheDocument()
  })

  it('should clear errors when fields are filled', async () => {
    renderFormStock({ initialValues, allowedActions, onSubmit })

    const saveButton = screen.getByText('Enregistrer')

    await userEvent.click(saveButton)

    expect(
      screen.getByText('La date de début est obligatoire')
    ).toBeInTheDocument()
    expect(
      screen.getByText('La date de fin est obligatoire')
    ).toBeInTheDocument()
    expect(screen.getByText('L’horaire est obligatoire')).toBeInTheDocument()
    expect(
      screen.getByText('Le nombre de participants est obligatoire')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Le prix total TTC est obligatoire')
    ).toBeInTheDocument()

    const userDateInput = format(addDays(new Date(), 5), FORMAT_ISO_DATE_ONLY)

    const startDateInput = screen.getByLabelText(/Date de début */)
    await userEvent.click(startDateInput)
    await waitFor(() => userEvent.type(startDateInput, userDateInput))

    const timeInput = screen.getByLabelText(/Horaire */)
    await userEvent.click(timeInput)
    await waitFor(() => userEvent.type(timeInput, '00:00'))

    await userEvent.type(
      screen.getByLabelText(/Nombre de participants */),
      '10'
    )
    await userEvent.type(screen.getByLabelText(/Prix total TTC */), '100')

    await waitFor(() => {
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
        screen.queryByText('Le nombre de participants est obligatoire')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Le prix total TTC est obligatoire')
      ).not.toBeInTheDocument()
    })
  })

  it('should automatically update end date input when the user edits the start date', async () => {
    renderFormStock({
      initialValues: {
        ...initialValues,
        startDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
      },
      allowedActions,
      onSubmit,
    })
    const userDateInput = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    const startDateInput = screen.getByLabelText(/Date de début */)
    await userEvent.click(startDateInput)
    await userEvent.clear(startDateInput)
    await waitFor(() => userEvent.type(startDateInput, userDateInput))
    const endDateInput = screen.getAllByLabelText(/Date de fin */)[1]
    expect(endDateInput).toHaveValue(userDateInput)
  })

  it('should not disable price and place when offer status is reimbursment', () => {
    renderFormStock({ initialValues, onSubmit, allowedActions: [] })

    const priceInput = screen.getByLabelText(/Prix total TTC/)
    const placeInput = screen.getByLabelText(/Nombre de participants/)

    expect(priceInput).toBeDisabled()
    expect(placeInput).toBeDisabled()
  })

  it('should not allow price to be greater than initial value', async () => {
    renderFormStock({
      initialValues: { ...initialValues, totalPrice: 1000 },
      onSubmit,
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
    })

    const priceInput = screen.getByLabelText(/Prix total TTC/)
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '10000')
    const saveButton = screen.getByText('Enregistrer')

    await userEvent.click(saveButton)

    expect(priceInput).toBeInvalid()
    expect(
      screen.getByText('Vous ne pouvez pas définir un prix plus élevé.')
    ).toBeInTheDocument()
  })

  it('should disable start date, end date and event time inputs when form access is read only', () => {
    renderFormStock({ initialValues, onSubmit, allowedActions: [] })

    const startDateInput = screen.getByLabelText(/Date de début */)
    const endDateInput = screen.getAllByLabelText(/Date de fin */)[1]
    const eventTimeInput = screen.getByLabelText(/Horaire */)

    expect(startDateInput).toBeDisabled()
    expect(endDateInput).toBeDisabled()
    expect(eventTimeInput).toBeDisabled()
  })

  it('should disable start date, end date, price and place and event time inputs when allowed actions CAN_EDIT_DATES and CAN_EDIT_DISCOUNT do not exist', () => {
    renderFormStock({ initialValues, onSubmit, allowedActions: [] })

    const startDateInput = screen.getByLabelText(/Date de début */)
    const endDateInput = screen.getAllByLabelText(/Date de fin */)[1]
    const eventTimeInput = screen.getByLabelText(/Horaire */)
    const placeInput = screen.getByLabelText(/Nombre de participants */)
    const priceInput = screen.getByLabelText(/Prix total TTC */)

    expect(placeInput).toBeDisabled()
    expect(priceInput).toBeDisabled()
    expect(startDateInput).toBeDisabled()
    expect(endDateInput).toBeDisabled()
    expect(eventTimeInput).toBeDisabled()
  })

  it('should not disable price, place number, start date, end date and event time when allowed actions CAN_EDIT_DISCOUNT and CAN_EDIT_DATES exist', () => {
    renderFormStock({ initialValues, onSubmit, allowedActions })

    const startDateInput = screen.getByLabelText(/Date de début */)
    const endDateInput = screen.getAllByLabelText(/Date de fin */)[1]
    const eventTimeInput = screen.getByLabelText(/Horaire */)
    const placeInput = screen.getByLabelText(/Nombre de participants */)
    const priceInput = screen.getByLabelText(/Prix total TTC */)

    expect(placeInput).not.toBeDisabled()
    expect(priceInput).not.toBeDisabled()
    expect(startDateInput).not.toBeDisabled()
    expect(endDateInput).not.toBeDisabled()
    expect(eventTimeInput).not.toBeDisabled()
  })
})
