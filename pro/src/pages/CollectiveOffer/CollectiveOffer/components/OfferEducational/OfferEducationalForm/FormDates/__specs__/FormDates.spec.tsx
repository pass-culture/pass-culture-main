import { yupResolver } from '@hookform/resolvers/yup'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addYears, format } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { getOfferEducationalValidationSchema } from '../../../validationSchema'
import { FormDates, FormDatesProps } from '../FormDates'

function renderFormDates(
  props: FormDatesProps,
  initialValues: OfferEducationalFormValues
) {
  function FormDatesWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
      resolver: yupResolver(getOfferEducationalValidationSchema(false)),
    })

    return (
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(() => {})}>
          <FormDates {...props} />
          <button type="submit">Submit</button>
        </form>
      </FormProvider>
    )
  }

  return renderWithProviders(<FormDatesWrapper />)
}

describe('FormDates', () => {
  const defaultProps: FormDatesProps = {
    disableForm: false,
    dateCreated: '',
  }

  it('should limit ending date to beggining date when value', () => {
    renderFormDates(defaultProps, {
      ...getDefaultEducationalValues(),
      isTemplate: true,
      beginningDate: new Date().toString(),
      endingDate: '',
      datesType: 'specific_dates',
      hour: '',
    })
    expect(screen.getByLabelText('Date de fin *')).toHaveAttribute(
      'min',
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
  })
  it('should limit starting date to date when value', () => {
    renderFormDates(
      { ...defaultProps, dateCreated: '2021-01-01' },
      {
        ...getDefaultEducationalValues(),
        isTemplate: true,
        beginningDate: new Date().toString(),
        endingDate: '',
        datesType: 'specific_dates',
        hour: '',
      }
    )
    expect(screen.getByLabelText('Date de début *')).toHaveAttribute(
      'min',
      format(new Date('2021-01-01'), FORMAT_ISO_DATE_ONLY)
    )
  })

  it.each([
    {
      beginningDate: new Date().toString(),
      endingDate: addYears(new Date(), 4).toString(),
    },
    {
      beginningDate: undefined,
      endingDate: undefined,
    },
  ])(
    'should not show the dates selection form section when the offer is permanent',
    (dates) => {
      renderFormDates(
        { ...defaultProps, dateCreated: '2021-01-01' },
        {
          ...getDefaultEducationalValues(),
          isTemplate: true,
          ...dates,
          datesType: 'permanent',
        }
      )
      expect(
        screen.queryByText(
          'Votre offre sera désactivée automatiquement à l’issue des dates précisées ci-dessous.'
        )
      ).not.toBeInTheDocument()
    }
  )

  it('should initially be set as a permanent offer', () => {
    renderFormDates(
      { ...defaultProps, dateCreated: '2021-01-01' },
      {
        ...getDefaultEducationalValues(),
        isTemplate: true,
      }
    )

    expect(
      screen.queryByText(
        'Votre offre sera mise en pause automatiquement à l’issue des dates précisées ci-dessous.'
      )
    ).not.toBeInTheDocument()
  })

  it('should not erase the selected dates when changing from specific dates offer to permanent and back', async () => {
    const startDate = format(new Date(), FORMAT_ISO_DATE_ONLY)

    renderFormDates(
      { ...defaultProps, dateCreated: '2021-01-01' },
      {
        ...getDefaultEducationalValues(),
        beginningDate: startDate,
        endingDate: addYears(new Date(), 4).toString(),
        datesType: 'specific_dates',
        isTemplate: true,
      }
    )

    const radioPermanent = screen.getByRole('radio', {
      name: 'Tout au long de l’année scolaire, l’offre est permanente',
    })

    const screenSpecific = screen.getByRole('radio', {
      name: 'À une date ou une période précise',
    })

    await userEvent.click(radioPermanent)

    await userEvent.click(screenSpecific)

    expect(screen.getByLabelText('Date de début *')).toHaveValue(startDate)
  })

  it('should set endingDate when the beginningDate changes', async () => {
    renderFormDates(
      { ...defaultProps, dateCreated: '2021-01-01' },
      {
        ...getDefaultEducationalValues(),
        isTemplate: true,
        datesType: 'specific_dates',
        beginningDate: '',
      }
    )

    const beginningInput = screen.getByLabelText('Date de début *')

    await userEvent.type(beginningInput, '2025-02-02')
    expect(screen.getByLabelText('Date de fin *')).toHaveValue('2025-02-02')
  })
})
