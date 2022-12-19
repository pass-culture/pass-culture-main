import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { SubmitButton } from 'ui-kit'

import FormNotifications from '../FormNotifications'

const renderFormNotifications = ({
  initialValues,
  onSubmit = jest.fn(),
}: {
  initialValues: Partial<IOfferEducationalFormValues>
  onSubmit: () => void
}) => {
  const validationSchema = yup.object().shape({
    notifications: yup.boolean(),
    notificationEmail: yup.string().when('notifications', {
      is: true,
      then: yup
        .string()
        .required('Veuillez renseigner une adresse e-mail')
        .email('Veuillez renseigner un e-mail valide'),
    }),
  })
  const rtlReturns = render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <FormNotifications disableForm={false} />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </form>
      )}
    </Formik>
  )

  return {
    ...rtlReturns,
    buttonSubmit: screen.getByRole('button', {
      name: 'Submit',
    }),
  }
}

describe('FormNotifications', () => {
  let initialValues: Partial<IOfferEducationalFormValues>
  const onSubmit = jest.fn()
  beforeEach(() => {
    initialValues = {
      notificationEmails: [''],
    }
  })

  it('should render notification mail with pro email value if provided', () => {
    initialValues = {
      notificationEmails: [''],
      email: 'test@example.com',
    }
    renderFormNotifications({ initialValues, onSubmit })

    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument()
  })

  it('should add notification mail input when button is clicked', async () => {
    initialValues = {
      notificationEmails: ['test@example.com'],
    }
    renderFormNotifications({ initialValues, onSubmit })
    let mailInputs = await screen.getAllByRole('textbox', {
      name: 'E-mail auquel envoyer les notifications',
    })
    const addInputButton = await screen.getByRole('button', {
      name: 'Ajouter un e-mail de notification',
    })
    expect(mailInputs.length).toEqual(1)
    await userEvent.click(addInputButton)
    mailInputs = await screen.getAllByRole('textbox', {
      name: 'E-mail auquel envoyer les notifications',
    })
    expect(mailInputs.length).toEqual(2)
  })
  it('should remove notification mail input when trash icon is clicked', async () => {
    initialValues = {
      notificationEmails: ['test@example.com', 'test2@example.com'],
    }
    renderFormNotifications({ initialValues, onSubmit })
    let mailInputs = await screen.getAllByRole('textbox', {
      name: 'E-mail auquel envoyer les notifications',
    })
    const removeInputIcon = await screen.getByRole('button', {
      name: "Supprimer l'email",
    })
    expect(mailInputs.length).toEqual(2)
    await userEvent.click(removeInputIcon)
    mailInputs = await screen.getAllByRole('textbox', {
      name: 'E-mail auquel envoyer les notifications',
    })
    expect(mailInputs.length).toEqual(1)
  })
})
