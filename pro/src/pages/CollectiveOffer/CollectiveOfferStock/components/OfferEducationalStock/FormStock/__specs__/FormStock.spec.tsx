import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { Form, Formik } from 'formik'

import {
  OfferEducationalStockFormValues,
  Mode,
  EducationalOfferType,
} from 'commons/core/OfferEducational/types'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { renderWithProviders, RenderWithProvidersOptions } from 'commons/utils/renderWithProviders'
import { Button } from 'ui-kit/Button/Button'

import { generateValidationSchema } from '../../validationSchema'
import { FormStock, FormStockProps } from '../FormStock'
import { renderWithProviders, RenderWithProvidersOptions } from 'commons/utils/renderWithProviders'

const renderFormStock = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
  options
}: {
  initialValues: OfferEducationalStockFormValues
  onSubmit: () => void
  props: FormStockProps
  options?: RenderWithProvidersOptions
}) => {
  return renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={generateValidationSchema(
        props.preventPriceIncrease,
        initialValues.totalPrice,
        false
      )}
    >
      <Form>
        <FormStock {...props} />
        <Button type="submit" isLoading={false}>
          Enregistrer
        </Button>
      </Form>
    </Formik>, 
    options
  )
}

describe('FormStock', () => {
  let initialValues: OfferEducationalStockFormValues
  const onSubmit = vi.fn()
  let props: FormStockProps

  beforeEach(() => {
    props = {
      mode: Mode.CREATION,
      preventPriceIncrease: false,
    }
    initialValues = {
      startDatetime: '',
      endDatetime: '',
      eventTime: '',
      numberOfPlaces: '',
      totalPrice: '',
      bookingLimitDatetime: '',
      priceDetail: '',
      educationalOfferType: EducationalOfferType.SHOWCASE,
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

  it('should automatically update end date input when the user edits the start date', async () => {
    renderFormStock({
      initialValues: {
        ...initialValues,
        startDatetime: format(new Date(), FORMAT_ISO_DATE_ONLY),
      },
      onSubmit,
      props: {
        mode: Mode.EDITION,
        canEditDiscount: false,
        canEditDates: true,
        preventPriceIncrease: false,
      },
    })
    const userDateInput = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    const startDatetimeInput = screen.getByLabelText('Date de début *')
    await userEvent.click(startDatetimeInput)
    await userEvent.clear(startDatetimeInput)
    await waitFor(() => userEvent.type(startDatetimeInput, userDateInput))
    const endDatetimeInput = screen.getByLabelText('Date de fin *')
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

    const priceInput = screen.getByLabelText('Prix total TTC *')
    const placeInput = screen.getByLabelText('Nombre de participants *')

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
        canEditDates: true,
        preventPriceIncrease: true,
      },
    })

    const priceInput = screen.getByLabelText('Prix total TTC *')
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
        disablePriceAndParticipantInputs: false,
        preventPriceIncrease: false,
      },
    })

    const startDatetimeInput = screen.getByLabelText('Date de début *')
    const endDatetimeInput = screen.getByLabelText('Date de fin *')
    const eventTimeInput = screen.getByLabelText('Horaire *')

    expect(startDatetimeInput).toBeDisabled()
    expect(endDatetimeInput).toBeDisabled()
    expect(eventTimeInput).toBeDisabled()
  })

  it('should disable start datetime, end datetime and event time inputs when allowedAction CAN_EDIT_DATES exist and ENABLE_COLLECTIVE_NEW_STATUSES is enabled', () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: true,
        canEditDates: false,
        preventPriceIncrease: false,
      },
      options: {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    })

    const startDatetimeInput = screen.getByLabelText('Date de début *')
    const endDatetimeInput = screen.getByLabelText('Date de fin *')
    const eventTimeInput = screen.getByLabelText('Horaire *')

    expect(startDatetimeInput).toBeDisabled()
    expect(endDatetimeInput).toBeDisabled()
    expect(eventTimeInput).toBeDisabled()
  })

  it('should not disable price and place number when allowedAction CAN_EDIT_DISCOUNT exist and ENABLE_COLLECTIVE_NEW_STATUSES is enabled', () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        canEditDiscount: true,
        canEditDates: false,
        preventPriceIncrease: false,
      },
      options: {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    })

    const placeInput = screen.getByLabelText('Nombre de participants *')
    const priceInput = screen.getByLabelText('Prix total TTC *')

    expect(placeInput).not.toBeDisabled()
    expect(priceInput).not.toBeDisabled()
  })
})
