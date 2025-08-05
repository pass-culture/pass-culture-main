import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { FormProvider, useForm } from 'react-hook-form'

import { FormNotifications } from '../FormNotifications'

function renderFormNotifications(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  function FormNotificationsWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
    })

    return (
      <FormProvider {...form}>
        <FormNotifications disableForm={false} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormNotificationsWrapper />)
}

describe('FormNotifications', () => {
  let initialValues: Partial<OfferEducationalFormValues>

  it('should add notification mail input when button is clicked', async () => {
    initialValues = {
      notificationEmails: [{ email: 'test@example.com' }],
    }
    renderFormNotifications(initialValues)

    expect(screen.getAllByRole('textbox')).toHaveLength(1)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Ajouter un email de notification',
      })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Ajouter un email de notification',
      })
    )

    expect(screen.getAllByRole('textbox')).toHaveLength(3)
  })

  it('should remove notification mail input when trash icon is clicked', async () => {
    initialValues = {
      notificationEmails: [
        { email: 'test@example.com' },
        { email: 'test2@example.com' },
      ],
    }
    renderFormNotifications(initialValues)

    const removeInputIcon = screen.getByRole('button', {
      name: 'Supprimer l’email',
    })
    expect(screen.getAllByRole('textbox')).toHaveLength(2)
    await userEvent.click(removeInputIcon)
    expect(screen.getAllByRole('textbox')).toHaveLength(1)
  })
})
