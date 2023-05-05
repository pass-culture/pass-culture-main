import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'
import { SubmitButton } from 'ui-kit'

import TicketWithdrawal, { ITicketWithdrawalProps } from '../TicketWithdrawal'
import validationSchema from '../validationSchema'

const renderTicketWithdrawal = ({
  props,
  initialValues,
  onSubmit = jest.fn(),
}: {
  props?: ITicketWithdrawalProps
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
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
  let initialValues: Partial<IOfferIndividualFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      subCategoryFields: ['withdrawalType', 'withdrawalDelay'],
      isEvent: true,
      withdrawalDetails: '',
      withdrawalType: undefined,
      withdrawalDelay: undefined,
    }
  })

  it('should display "withdrawalDelay" fields depending of withdrawalType selected value.', async () => {
    await renderTicketWithdrawal({
      initialValues,
      onSubmit,
    })

    // should contain sent date information when tickets are sent by mail
    await userEvent.click(await screen.findByText('Envoi par e-mail'))
    expect(await screen.findByText('Date d’envoi')).toBeInTheDocument()

    // should contain withdrawal hour information when tickets are to withdraw on place
    await userEvent.click(
      await screen.findByText('Retrait sur place (guichet, comptoir...)')
    )
    expect(await screen.findByText('Heure de retrait')).toBeInTheDocument()

    await userEvent.click(await screen.findByText('Évènement sans billet'))
    expect(await screen.queryByText('Date d’envoi')).not.toBeInTheDocument()
    expect(await screen.queryByText('Heure de retrait')).not.toBeInTheDocument()
  })

  it('should display an error when withdrawalType is empty', async () => {
    renderTicketWithdrawal({
      initialValues,
      onSubmit,
    })

    expect(
      screen.queryByText('Veuillez sélectionner l’une de ces options')
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Veuillez sélectionner l’une de ces options')
    ).toBeInTheDocument()
  })

  it('should disable read only fields', () => {
    const props = { readOnlyFields: ['withdrawalType', 'withdrawalDelay'] }

    renderTicketWithdrawal({
      props,
      initialValues,
      onSubmit,
    })

    expect(screen.getByLabelText('Envoi par e-mail')).toBeDisabled()
    expect(screen.getByLabelText('Évènement sans billet')).toBeDisabled()
    expect(
      screen.getByLabelText('Retrait sur place (guichet, comptoir...)')
    ).toBeDisabled()
  })
})
