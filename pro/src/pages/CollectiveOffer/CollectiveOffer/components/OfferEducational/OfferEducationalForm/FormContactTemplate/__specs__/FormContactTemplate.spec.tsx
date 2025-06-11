import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormContactTemplate } from '../FormContactTemplate'

function renderFormContactTemplate(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  function FormContactTemplateWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
    })

    return (
      <FormProvider {...form}>
        <FormContactTemplate disableForm={false} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormContactTemplateWrapper />)
}

describe('FormContactTemplate', () => {
  it('should show the email form when the contact email checkbox is checked', async () => {
    renderFormContactTemplate({ isTemplate: true })
    expect(
      screen.queryByRole('textbox', {
        name: 'Email de contact',
      })
    ).not.toBeInTheDocument()

    const emailCheckbox = screen.getByRole('checkbox', { name: 'Par email' })
    await userEvent.click(emailCheckbox)

    expect(
      screen.getByRole('textbox', {
        name: 'Adresse email *',
      })
    ).toBeInTheDocument()
  })

  it('should show the phone form when the contact phone checkbox is checked', async () => {
    renderFormContactTemplate({ isTemplate: true })
    expect(screen.queryByText('Numéro de téléphone')).not.toBeInTheDocument()

    const phoneCheckbox = screen.getByRole('checkbox', {
      name: 'Par téléphone',
    })
    await userEvent.click(phoneCheckbox)

    expect(
      screen.getByRole('textbox', { name: 'Numéro de téléphone' })
    ).toBeInTheDocument()
  })

  it('should show the custom contact form when the custom contact checkbox is checked', async () => {
    renderFormContactTemplate({ isTemplate: true })
    expect(screen.queryByText('mon propre formulaire')).not.toBeInTheDocument()

    const customContactCheckbox = screen.getByRole('checkbox', {
      name: /un formulaire/,
    })
    await userEvent.click(customContactCheckbox)

    expect(screen.getByText('mon propre formulaire')).toBeInTheDocument()
  })
})
