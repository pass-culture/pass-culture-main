import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormContactTemplateCustomForm } from '../FormContactTemplateCustomForm'

function renderFormContactCustomForm(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  function FormContactTemplateCustomFormWrapper() {
    const form = useForm({
      defaultValues: initialValues,
    })

    return (
      <FormProvider {...form}>
        <FormContactTemplateCustomForm disableForm={false} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormContactTemplateCustomFormWrapper />)
}

describe('FormContactTemplateCustomForm', () => {
  it('should show the radio buttons form', () => {
    renderFormContactCustomForm()

    expect(
      screen.getByRole('radio', { name: 'Le formulaire standard' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('radio', {
        name: 'Mon propre formulaire',
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
        name: 'URL de mon formulaire de contact *',
      })
    ).toBeInTheDocument()
  })

  it('should whitch the type of contact form', async () => {
    renderFormContactCustomForm({
      ...getDefaultEducationalValues(),
      contactFormType: 'url',
      contactUrl: 'http://www.test-url.com',
    })

    await userEvent.click(screen.getByLabelText('Le formulaire standard'))

    expect(
      screen.queryByRole('textbox', {
        name: 'URL de mon formulaire de contact *',
      })
    ).not.toBeInTheDocument()
  })
})
