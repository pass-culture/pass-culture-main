import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addYears } from 'date-fns'
import format from 'date-fns/format'
import { Formik } from 'formik'

import {
  DEFAULT_EAC_FORM_VALUES,
  OfferEducationalFormValues,
} from 'core/OfferEducational'
import { getOfferEducationalValidationSchema } from 'screens/OfferEducational/validationSchema'
import { SubmitButton } from 'ui-kit'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'

import FormDates, { FormDatesProps } from '../FormDates'

const renderFormDates = (
  props: FormDatesProps,
  initialValues: OfferEducationalFormValues
) => {
  render(
    <Formik
      initialValues={initialValues}
      onSubmit={vi.fn()}
      validationSchema={getOfferEducationalValidationSchema(false)}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <FormDates {...props} />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </form>
      )}
    </Formik>
  )
}

describe('FormDates', () => {
  const defaultProps: FormDatesProps = {
    disableForm: false,
    dateCreated: '',
  }
  it('should display error message if ending date is more than 3 years from today', async () => {
    renderFormDates(defaultProps, {
      ...DEFAULT_EAC_FORM_VALUES,
      isTemplate: true,
      beginningDate: '',
      endingDate: addYears(new Date(), 4).toString(),
      hour: '',
    })
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(
      screen.getByText('La date de fin que vous avez choisie est trop éloignée')
    ).toBeInTheDocument()
  })

  it('should limit ending date to beggining date when value', () => {
    renderFormDates(defaultProps, {
      ...DEFAULT_EAC_FORM_VALUES,
      isTemplate: true,
      beginningDate: new Date().toString(),
      endingDate: '',
      hour: '',
    })
    expect(screen.getByLabelText('Date de fin')).toHaveAttribute(
      'min',
      format(new Date(), FORMAT_ISO_DATE_ONLY)
    )
  })
  it('should limit starting date to date when value', () => {
    renderFormDates(
      { ...defaultProps, dateCreated: '2021-01-01' },
      {
        ...DEFAULT_EAC_FORM_VALUES,
        isTemplate: true,
        beginningDate: new Date().toString(),
        endingDate: '',
        hour: '',
      }
    )
    expect(screen.getByLabelText('Date de début')).toHaveAttribute(
      'min',
      format(new Date('2021-01-01'), FORMAT_ISO_DATE_ONLY)
    )
  })
})
