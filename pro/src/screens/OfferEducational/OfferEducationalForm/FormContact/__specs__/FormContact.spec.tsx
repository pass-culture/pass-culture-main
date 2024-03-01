import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import {
  DEFAULT_EAC_FORM_VALUES,
  OfferEducationalFormValues,
} from 'core/OfferEducational'
import { renderWithProviders } from 'utils/renderWithProviders'

import FormContact from '../FormContact'

function renderFormContact(
  initialValues: Partial<OfferEducationalFormValues> = DEFAULT_EAC_FORM_VALUES
) {
  return renderWithProviders(
    <Formik
      initialValues={{ ...DEFAULT_EAC_FORM_VALUES, ...initialValues }}
      onSubmit={() => {}}
    >
      <FormContact disableForm={false} />
    </Formik>
  )
}

describe('FormContact', () => {
  it('should show the normal contact form', () => {
    renderFormContact({})
    expect(
      screen.queryByText(
        'Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre : *'
      )
    ).not.toBeInTheDocument()
  })

  it('should show the normal contact form if the offer is bookable', () => {
    renderFormContact({ isTemplate: false })
    expect(
      screen.queryByText(
        'Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre : *'
      )
    ).not.toBeInTheDocument()
  })
})
