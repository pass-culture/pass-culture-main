import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormContactTemplate } from '../FormContactTemplate'

function renderFormContact(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  return renderWithProviders(
    <Formik
      initialValues={{ ...getDefaultEducationalValues(), ...initialValues }}
      onSubmit={() => {}}
    >
      <FormContactTemplate disableForm={false} />
    </Formik>
  )
}

describe('FormContactTemplate', () => {
  it('should show the email form when the contact email checkbox is checked', async () => {
    renderFormContact({ isTemplate: true })
    expect(
      screen.queryByRole('textbox', {
        name: 'Email de contact',
      })
    ).not.toBeInTheDocument()

    const emailCheckbox = screen.getByRole('checkbox', { name: 'Par email' })
    await userEvent.click(emailCheckbox)

    expect(
      screen.getByRole('textbox', {
        name: 'Adresse email',
      })
    ).toBeInTheDocument()
  })

  it('should show the phone form when the contact phone checkbox is checked', async () => {
    renderFormContact({ isTemplate: true })
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
    renderFormContact({ isTemplate: true })
    expect(screen.queryByText('mon propre formulaire')).not.toBeInTheDocument()

    const customContactCheckbox = screen.getByRole('checkbox', {
      name: /un formulaire/,
    })
    await userEvent.click(customContactCheckbox)

    expect(screen.getByText('mon propre formulaire')).toBeInTheDocument()
  })
})
