import { yupResolver } from '@hookform/resolvers/yup'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import {
  Mode,
  OfferEducationalStockFormValues,
} from 'commons/core/OfferEducational/types'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { addDays, format } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'

import { generateValidationSchema } from '../../validationSchema'
import { FormStock, FormStockProps } from '../FormStock'

function renderFormStock({
  initialValues,
  onSubmit = vi.fn(),
  props,
  options,
}: {
  initialValues: OfferEducationalStockFormValues
  onSubmit: () => void
  props: FormStockProps
  options?: RenderWithProvidersOptions
}) {
  const preventPriceIncrease = props.preventPriceIncrease

  function FormStockWrapper() {
    const form = useForm({
      defaultValues: initialValues,
      resolver: yupResolver<OfferEducationalStockFormValues>(
        generateValidationSchema(
          preventPriceIncrease,
          initialValues.totalPrice,
          false
        )
      ),
      mode: 'onTouched',
    })

    return (
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormStock {...props} />
          <Button type="submit" isLoading={false}>
            Enregistrer
          </Button>
        </form>
      </FormProvider>
    )
  }

  return renderWithProviders(<FormStockWrapper />, options)
}

describe('FormStock', () => {
  let initialValues: OfferEducationalStockFormValues
  const onSubmit = vi.fn()
  let props: FormStockProps

  beforeEach(() => {
    props = {
      mode: Mode.CREATION,
      canEditDiscount: false,
      canEditDates: false,
      preventPriceIncrease: false,
    }
    initialValues = {
      startDatetime: '',
      endDatetime: '',
      eventTime: '',
      numberOfPlaces: null,
      totalPrice: null,
      bookingLimitDatetime: '',
      priceDetail: '',
    }
  })

  it('should display an error when the field is empty', async () => {
    renderFormStock({ initialValues: initialValues, onSubmit, props })

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
  })

  it('should clear errors when fields are filled', async () => {
    props.canEditDates = true
    props.canEditDiscount = true

    renderFormStock({ initialValues, onSubmit, props })

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

    const startDatetimeInput = screen.getByLabelText('Date de début')
    await userEvent.click(startDatetimeInput)
    await waitFor(() => userEvent.type(startDatetimeInput, userDateInput))

    const timeInput = screen.getByLabelText('Horaire')
    await userEvent.click(screen.getByLabelText('Horaire'))
    await waitFor(() => userEvent.type(timeInput, '00:00'))

    await userEvent.type(screen.getByLabelText('Nombre de participants'), '10')
    await userEvent.type(screen.getByLabelText('Prix total TTC'), '100')

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
        startDatetime: format(new Date(), FORMAT_ISO_DATE_ONLY),
      },
      onSubmit,
      props: {
        mode: Mode.EDITION,
        canEditDiscount: true,
        canEditDates: true,
        preventPriceIncrease: false,
      },
    })
    const userDateInput = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    const startDatetimeInput = screen.getByLabelText('Date de début')
    await userEvent.click(startDatetimeInput)
    await userEvent.clear(startDatetimeInput)
    await waitFor(() => userEvent.type(startDatetimeInput, userDateInput))
    const endDatetimeInput = screen.getAllByLabelText(/Date de fin/)[1]
    expect(endDatetimeInput).toHaveValue(userDateInput)
  })

  it('should not disable price and place when offer status is reimbursment', () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: false,
        canEditDates: false,
        preventPriceIncrease: true,
      },
    })

    const priceInput = screen.getByLabelText('Prix total TTC')
    const placeInput = screen.getByLabelText('Nombre de participants')

    expect(priceInput).toBeDisabled()
    expect(placeInput).toBeDisabled()
  })

  it('should not allow price to be greater than initial value', async () => {
    renderFormStock({
      initialValues: { ...initialValues, totalPrice: 1000 },
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: true,
        canEditDates: false,
        preventPriceIncrease: true,
      },
    })

    const priceInput = screen.getByLabelText('Prix total TTC')
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '10000')
    const saveButton = screen.getByText('Enregistrer')

    await userEvent.click(saveButton)

    expect(priceInput).toBeInvalid()
    expect(
      screen.getByText('Vous ne pouvez pas définir un prix plus élevé.')
    ).toBeInTheDocument()
  })

  it('should disable start datetime, end datetime and event time inputs when form access is read only', () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: false,
        canEditDates: false,
        preventPriceIncrease: false,
      },
    })

    const startDatetimeInput = screen.getByLabelText('Date de début')
    const endDatetimeInput = screen.getAllByLabelText(/Date de fin/)[1]
    const eventTimeInput = screen.getByLabelText('Horaire')

    expect(startDatetimeInput).toBeDisabled()
    expect(endDatetimeInput).toBeDisabled()
    expect(eventTimeInput).toBeDisabled()
  })

  it('should disable start datetime, end datetime, price and place and event time inputs when allowed actions CAN_EDIT_DATES and CAN_EDIT_DISCOUNT do not exist', () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: false,
        canEditDates: false,
        preventPriceIncrease: false,
      },
    })

    const startDatetimeInput = screen.getByLabelText('Date de début')
    const endDatetimeInput = screen.getAllByLabelText(/Date de fin/)[1]
    const eventTimeInput = screen.getByLabelText('Horaire')
    const placeInput = screen.getByLabelText('Nombre de participants')
    const priceInput = screen.getByLabelText('Prix total TTC')

    expect(placeInput).toBeDisabled()
    expect(priceInput).toBeDisabled()
    expect(startDatetimeInput).toBeDisabled()
    expect(endDatetimeInput).toBeDisabled()
    expect(eventTimeInput).toBeDisabled()
  })

  it('should not disable price, place number, start datetime, end datetime and event time when allowed actions CAN_EDIT_DISCOUNT and CAN_EDIT_DATES exist', () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: true,
        canEditDates: true,
        preventPriceIncrease: false,
      },
    })

    const startDatetimeInput = screen.getByLabelText('Date de début')
    const endDatetimeInput = screen.getAllByLabelText(/Date de fin/)[1]
    const eventTimeInput = screen.getByLabelText('Horaire')
    const placeInput = screen.getByLabelText('Nombre de participants')
    const priceInput = screen.getByLabelText('Prix total TTC')

    expect(placeInput).not.toBeDisabled()
    expect(priceInput).not.toBeDisabled()
    expect(startDatetimeInput).not.toBeDisabled()
    expect(endDatetimeInput).not.toBeDisabled()
    expect(eventTimeInput).not.toBeDisabled()
  })
})
