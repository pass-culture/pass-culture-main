import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import { Provider } from 'react-redux'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import { configureTestStore } from 'store/testUtils'
import { SubmitButton } from 'ui-kit'

import Notifications from '../Notifications'
import validationSchema from '../validationSchema'

const renderNotifications = ({
  initialValues,
  onSubmit = jest.fn(),
}: {
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
}) => {
  const store = {
    user: {
      currentUser: {
        email: 'email@example.com',
      },
      initialized: true,
    },
  }
  return render(
    <Provider store={configureTestStore(store)}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={yup.object().shape(validationSchema)}
      >
        <Form>
          <Notifications />
          <SubmitButton className="primary-button" isLoading={false}>
            Submit
          </SubmitButton>
        </Form>
      </Formik>
    </Provider>
  )
}

describe('OfferIndividual section: Notifications', () => {
  let initialValues: Partial<IOfferIndividualFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      receiveNotificationEmails: false,
      bookingEmail: '',
    }
  })

  it('should submit valid form', async () => {
    await renderNotifications({
      initialValues,
      onSubmit,
    })
    await userEvent.click(
      screen.getByText('Être notifié par email des réservations')
    )

    await userEvent.click(screen.getByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      { bookingEmail: 'email@example.com', receiveNotificationEmails: true },
      expect.anything()
    )
  })

  it('should display bookingEmail field with default value depending of receiveNotificationEmails.', async () => {
    await renderNotifications({
      initialValues,
      onSubmit,
    })
    expect(await screen.findByText('Notifications')).toBeInTheDocument()
    expect(
      await screen.findByText('Être notifié par email des réservations')
    ).toBeInTheDocument()
    expect(
      await screen.queryByText('Email auquel envoyer les notifications :')
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByText('Être notifié par email des réservations')
    )
    expect(
      await screen.findByText('Email auquel envoyer les notifications :')
    ).toBeInTheDocument()
    expect(
      await screen.getByDisplayValue('email@example.com')
    ).toBeInTheDocument()
  })

  it('should display errors when bookingEmail is empty or wrong email', async () => {
    renderNotifications({
      initialValues,
      onSubmit,
    })

    await userEvent.click(
      screen.getByText('Être notifié par email des réservations')
    )
    const bookingEmailInput = screen.getByLabelText(
      'Email auquel envoyer les notifications :'
    )

    // when email is empty
    await userEvent.clear(bookingEmailInput)
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Veuillez renseigner une adresse email')
    ).toBeInTheDocument()

    // when email is wrong
    await userEvent.click(bookingEmailInput)
    await userEvent.paste('not an email')
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Veuillez renseigner un email valide')
    ).toBeInTheDocument()
  })
})
