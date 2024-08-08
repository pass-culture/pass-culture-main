import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import { FormContactTemplate } from '../FormContactTemplate'

function renderFormContact(
  initialValues: Partial<OfferEducationalFormValues> = DEFAULT_EAC_FORM_VALUES
) {
  return renderWithProviders(
    <Formik
      initialValues={{ ...DEFAULT_EAC_FORM_VALUES, ...initialValues }}
      onSubmit={() => {}}
    >
      <FormContactTemplate disableForm={false} />
    </Formik>
  )
}

describe('FormContactTemplate', () => {
  it('should show the checkbox group contact form if the FF is active', () => {
    renderFormContact({ isTemplate: true })
    expect(
      screen.getByText(
        'Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre : *'
      )
    ).toBeInTheDocument()
  })

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
        name: 'Email de contact',
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

    expect(screen.getByText('Numéro de téléphone')).toBeInTheDocument()
  })

  it('should show the custom contact form when the custom contact checkbox is checked', async () => {
    renderFormContact({ isTemplate: true })
    expect(
      screen.queryByText('mon propre formulaire accessible à cette URL')
    ).not.toBeInTheDocument()

    const customContactCheckbox = screen.getByRole('checkbox', {
      name: /un formulaire/,
    })
    await userEvent.click(customContactCheckbox)

    expect(
      screen.getByText('mon propre formulaire accessible à cette URL')
    ).toBeInTheDocument()
  })
})
