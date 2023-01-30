import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import { Provider } from 'react-redux'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { configureTestStore } from 'store/testUtils'
import { SubmitButton } from 'ui-kit'

import Notifications, { INotifications } from '../Notifications'
import validationSchema from '../validationSchema'

const renderNotifications = ({
  props,
  initialValues,
  onSubmit = jest.fn(),
  venueBookingEmail,
}: {
  props?: INotifications
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
  venueBookingEmail?: string | null
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
          <Notifications {...props} venueBookingEmail={venueBookingEmail} />
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
      screen.getByText('Être notifié par e-mail des réservations')
    )

    await userEvent.click(screen.getByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      { bookingEmail: 'email@example.com', receiveNotificationEmails: true },
      expect.anything()
    )
  })

  it('should display bookingEmail field with default user mail value depending of receiveNotificationEmails.', async () => {
    await renderNotifications({
      initialValues,
      onSubmit,
    })
    expect(await screen.findByText('Notifications')).toBeInTheDocument()
    expect(
      await screen.findByText('Être notifié par e-mail des réservations')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('E-mail auquel envoyer les notifications')
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByText('Être notifié par e-mail des réservations')
    )
    expect(
      await screen.findByText('E-mail auquel envoyer les notifications')
    ).toBeInTheDocument()
    expect(screen.getByDisplayValue('email@example.com')).toBeInTheDocument()
  })

  it('should display bookingEmail field with venueBookingMail default value depending of receiveNotificationEmails.', async () => {
    await renderNotifications({
      initialValues,
      onSubmit,
      venueBookingEmail: 'venue@exemple.com',
    })
    expect(await screen.findByText('Notifications')).toBeInTheDocument()
    expect(
      await screen.findByText('Être notifié par e-mail des réservations')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('E-mail auquel envoyer les notifications')
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByText('Être notifié par e-mail des réservations')
    )
    expect(
      await screen.findByText('E-mail auquel envoyer les notifications')
    ).toBeInTheDocument()
    expect(screen.getByDisplayValue('venue@exemple.com')).toBeInTheDocument()
  })

  it('should display bookingEmail field with value already set depending of receiveNotificationEmails.', async () => {
    initialValues.bookingEmail = 'customMail@exemple.com'
    await renderNotifications({
      initialValues,
      onSubmit,
      venueBookingEmail: 'venue@exemple.com',
    })
    expect(await screen.findByText('Notifications')).toBeInTheDocument()
    expect(
      await screen.findByText('Être notifié par e-mail des réservations')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('E-mail auquel envoyer les notifications')
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByText('Être notifié par e-mail des réservations')
    )
    expect(
      await screen.findByText('E-mail auquel envoyer les notifications')
    ).toBeInTheDocument()
    expect(
      screen.getByDisplayValue('customMail@exemple.com')
    ).toBeInTheDocument()
  })

  it('should display errors when bookingEmail is empty or wrong email', async () => {
    renderNotifications({
      initialValues,
      onSubmit,
    })

    await userEvent.click(
      screen.getByText('Être notifié par e-mail des réservations')
    )
    const bookingEmailInput = screen.getByLabelText(
      'E-mail auquel envoyer les notifications'
    )

    // when email is empty
    await userEvent.clear(bookingEmailInput)
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Veuillez renseigner une adresse e-mail')
    ).toBeInTheDocument()

    // when email is wrong
    await userEvent.click(bookingEmailInput)
    await userEvent.paste('not an email')
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Veuillez renseigner un e-mail valide')
    ).toBeInTheDocument()
  })

  it('should disable read only fields', () => {
    const props = {
      readOnlyFields: ['receiveNotificationEmails'],
    }
    renderNotifications({
      props,
      initialValues,
      onSubmit,
    })

    expect(
      screen.getByLabelText('Être notifié par e-mail des réservations')
    ).toBeDisabled()
  })

  it('should disable bookingEmail read only fields', async () => {
    const props = {
      readOnlyFields: ['bookingEmail'],
    }

    renderNotifications({
      props,
      initialValues,
      onSubmit,
    })

    await userEvent.click(
      screen.getByText('Être notifié par e-mail des réservations')
    )

    expect(
      screen.getByLabelText('E-mail auquel envoyer les notifications')
    ).toBeDisabled()
  })
})
