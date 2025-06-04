import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormContactTemplateCustomForm } from '../FormContactTemplateCustomForm'

function renderFormContactCustomForm(
  initialValues: OfferEducationalFormValues = getDefaultEducationalValues()
) {
  return renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={() => {}}>
      <FormContactTemplateCustomForm disableForm={false} />
    </Formik>
  )
}

describe('FormContactTemplateCustomForm', () => {
  it('should show the radio buttons form', () => {
    renderFormContactCustomForm()

    expect(
      screen.getByRole('radio', { name: 'le formulaire standard' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('radio', {
        name: 'mon propre formulaire',
      })
    ).toBeInTheDocument()
  })

  it("should have the custom form selected initially if it's the one checked in the form values", async () => {
    renderFormContactCustomForm({
      ...getDefaultEducationalValues(),
      contactFormType: 'url',
      contactUrl: 'http://www.test-url.com',
    })

    expect(
      await screen.findByRole('textbox', {
        name: 'URL de mon formulaire de contact',
      })
    ).toBeInTheDocument()
  })
})
