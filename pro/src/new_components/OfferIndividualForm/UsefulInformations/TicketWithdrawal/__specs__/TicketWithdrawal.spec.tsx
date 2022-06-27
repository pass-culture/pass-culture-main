import '@testing-library/jest-dom'

import * as yup from 'yup'

import { Form, Formik } from 'formik'
import TicketWithdrawal, { ITicketWithdrawalProps } from '../TicketWithdrawal'
import { render, screen } from '@testing-library/react'

import React from 'react'
import { SubmitButton } from 'ui-kit'
import userEvent from '@testing-library/user-event'
import { validationSchema } from '../'

interface IInitialValues {
  isEvent?: boolean
  subCategoryId: string
  withdrawalDetails: string
  withdrawalType: string
  withdrawalDelay: string
}

const renderTicketWithdrawal = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IInitialValues
  onSubmit: () => void
  props: ITicketWithdrawalProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <TicketWithdrawal {...props} />
        <SubmitButton className="primary-button" isLoading={false}>
          Submit
        </SubmitButton>
      </Form>
    </Formik>
  )
}

describe('OfferIndividual section: TicketWithdrawal', () => {
  let initialValues: IInitialValues
  let props: ITicketWithdrawalProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      isEvent: true,
      subCategoryId: '',
      withdrawalDetails: '',
      withdrawalType: '',
      withdrawalDelay: '',
    }
    props = {
      subCategories: [],
    }
  })

  it('should display "withdrawalDelay" fields depending of withdrawalType selected value.', async () => {
    // for an event subCategory
    await renderTicketWithdrawal({
      initialValues,
      onSubmit,
      props,
    })

    // should contain sent date information when tickets are sent by mail
    await userEvent.click(await screen.findByText('Envoi par e-mail'))
    expect(await screen.findByText('Date d’envoi')).toBeInTheDocument()

    // should contain withdrawal hour information when tickets are to withdraw on place
    await userEvent.click(
      await screen.findByText('Retrait sur place (guichet, comptoir ...)')
    )
    expect(await screen.findByText('Heure de retrait')).toBeInTheDocument()
  })

  it('should display an error when withdrawalType is empty', async () => {
    renderTicketWithdrawal({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      screen.queryByText('Vous devez cocher l’une des options ci-dessus')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Vous devez choisir l’une des options ci-dessus')
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.getByText('Vous devez cocher l’une des options ci-dessus')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Vous devez choisir l’une des options ci-dessus')
    ).not.toBeInTheDocument()
  })

  it('should display an error when withdrawalDelay is empty and withdrawalType for e-mail', async () => {
    renderTicketWithdrawal({
      initialValues,
      onSubmit,
      props,
    })

    await userEvent.click(screen.getByText('Envoi par e-mail'))
    expect(
      screen.queryByText('Vous devez cocher l’une des options ci-dessus')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Vous devez choisir l’une des options ci-dessus')
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText('Date d’envoi'))
    // FIXME: select field need two click outside in order to trigger validation.
    await userEvent.tab()
    await userEvent.tab()
    expect(
      screen.queryByText('Vous devez cocher l’une des options ci-dessus')
    ).not.toBeInTheDocument()
    expect(
      screen.getByText('Vous devez choisir l’une des options ci-dessus')
    ).toBeInTheDocument()
  })

  it('should display an error when withdrawalDelay is empty and withdrawalType on place', async () => {
    renderTicketWithdrawal({
      initialValues,
      onSubmit,
      props,
    })

    await userEvent.click(
      screen.getByText('Retrait sur place (guichet, comptoir ...)')
    )
    expect(
      screen.queryByText('Vous devez cocher l’une des options ci-dessus')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Vous devez choisir l’une des options ci-dessus')
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText('Heure de retrait'))
    // FIXME: select field need two click outside in order to trigger validation.
    await userEvent.tab()
    await userEvent.tab()

    expect(
      screen.queryByText('Vous devez cocher l’une des options ci-dessus')
    ).not.toBeInTheDocument()
    expect(
      screen.getByText('Vous devez choisir l’une des options ci-dessus')
    ).toBeInTheDocument()
  })
})
