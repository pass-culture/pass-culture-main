import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { Button } from 'ui-kit/Button/Button'

import {
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
} from '../constants'
import { TicketWithdrawalProps, TicketWithdrawal } from '../TicketWithdrawal'
import { validationSchema } from '../validationSchema'

const renderTicketWithdrawal = ({
  props,
  initialValues,
  onSubmit = vi.fn(),
}: {
  props?: TicketWithdrawalProps
  initialValues: Partial<IndividualOfferFormValues>
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
        <Button type="submit" isLoading={false}>
          Submit
        </Button>
      </Form>
    </Formik>
  )
}

describe('IndividualOffer section: TicketWithdrawal', () => {
  let initialValues: Partial<IndividualOfferFormValues>
  const onSubmit = vi.fn()

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
    renderTicketWithdrawal({ initialValues, onSubmit })

    // should contain sent date information when tickets are sent by mail
    await userEvent.click(
      await screen.findByText('Les billets seront envoyés par email')
    )
    expect(await screen.findByText('Date d’envoi *')).toBeInTheDocument()

    for (const options of ticketSentDateOptions) {
      const optionEl = screen.getByText(options.label)
      expect(optionEl).toBeInTheDocument()
      expect(optionEl).toHaveValue(options.value)
    }

    // should contain withdrawal hour information when tickets are to withdraw on place
    await userEvent.click(
      await screen.findByText('Retrait sur place (guichet, comptoir...)')
    )
    expect(await screen.findByText('Heure de retrait *')).toBeInTheDocument()

    for (const options of ticketWithdrawalHourOptions) {
      const optionEl = screen.getByText(options.label)
      expect(optionEl).toBeInTheDocument()
      expect(optionEl).toHaveValue(options.value)
    }

    await userEvent.click(
      await screen.findByText('Aucun billet n’est nécessaire')
    )
    expect(screen.queryByText('Date d’envoi')).not.toBeInTheDocument()
    expect(screen.queryByText('Heure de retrait')).not.toBeInTheDocument()
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

    expect(
      screen.getByLabelText('Les billets seront envoyés par email')
    ).toBeDisabled()
    expect(
      screen.getByLabelText('Aucun billet n’est nécessaire')
    ).toBeDisabled()
    expect(
      screen.getByLabelText('Retrait sur place (guichet, comptoir...)')
    ).toBeDisabled()
  })
  it('should disable read if offer has a withdrawal type "IN_APP"', () => {
    const props = { readOnlyFields: ['withdrawalType', 'withdrawalDelay'] }
    initialValues = {
      subCategoryFields: ['withdrawalType', 'withdrawalDelay'],
      isEvent: true,
      withdrawalDetails: '',
      withdrawalType: WithdrawalTypeEnum.IN_APP,
      withdrawalDelay: undefined,
    }

    renderTicketWithdrawal({
      props,
      initialValues,
      onSubmit,
    })

    expect(
      screen.getByLabelText('Les billets seront envoyés par email')
    ).toBeDisabled()
    expect(
      screen.getByLabelText('Aucun billet n’est nécessaire')
    ).toBeDisabled()
    expect(
      screen.getByLabelText('Retrait sur place (guichet, comptoir...)')
    ).toBeDisabled()
    expect(
      screen.getByLabelText('Les billets seront affichés dans l’application')
    ).toBeDisabled()
  })
})
