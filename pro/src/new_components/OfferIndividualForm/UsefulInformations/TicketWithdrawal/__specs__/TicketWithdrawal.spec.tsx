import '@testing-library/jest-dom'

import * as yup from 'yup'

import TicketWithdrawal, { ITicketWithdrawalProps } from '../TicketWithdrawal'
import { render, screen, waitFor } from '@testing-library/react'
import { CATEGORY_STATUS } from 'core/Offers'
import { Formik } from 'formik'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import React from 'react'
import userEvent from '@testing-library/user-event'
import { validationSchema } from '../'

interface IInitialValues {
  offererId: string
  venueId: string
  subcategoryId: string
  withdrawalDetails: string
  ticketWithdrawal: string
  ticketSentDate: string
  ticketWithdrawalHour: string
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
      <TicketWithdrawal {...props} />
    </Formik>
  )
}

describe('OfferIndividual section: TicketWithdrawal', () => {
  let initialValues: IInitialValues
  let props: ITicketWithdrawalProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    const subCategories = [
      {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie de A',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'B-A',
        categoryId: 'B',
        proLabel: 'Sous catégorie de B',
        isEvent: false,
        conditionalFields: ['musicType', 'musicSubType'],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'C-A',
        categoryId: 'C',
        proLabel: 'Sous catégorie de C',
        isEvent: false,
        conditionalFields: ['showType', 'showSubType'],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]
    initialValues = {
      offererId: '',
      venueId: '',
      subcategoryId: '',
      withdrawalDetails: '',
      ticketWithdrawal: '',
      ticketSentDate: '',
      ticketWithdrawalHour: '',
    }
    props = {
      subCategories,
    }
  })

  it('should contain withdrawal ticket informations when subcategory is an event', async () => {
    // for an event subCategory
    initialValues.subcategoryId = 'A-A'

    renderTicketWithdrawal({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      await screen.findByText(
        'Comment les billets, places seront-ils transmis ?'
      )
    ).toBeInTheDocument()

    // should contain sent date information when tickets are sent by mail
    await userEvent.click(await screen.findByText('Envoi par e-mail'))
    expect(await screen.findByText('Date d’envoi')).toBeInTheDocument()

    // should contain withdrawal hour information when tickets are to withdraw on place
    await userEvent.click(
      await screen.findByText('Retrait sur place (guichet, comptoir ...)')
    )
    expect(await screen.findByText('Heure de retrait')).toBeInTheDocument()
  })

  it('should display an error when the user has not filled all required fields', async () => {
    // for an event subCategory
    initialValues.subcategoryId = 'A-A'

    renderTicketWithdrawal({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      screen.queryByText('Vous devez cocher l’une des options ci-dessus')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Vous devez choisir une date d’envoi')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Vous devez choisir une heure de retrait')
    ).not.toBeInTheDocument()

    await userEvent.click(
      await screen.findByText(
        'Comment les billets, places seront-ils transmis ?'
      )
    )
    await userEvent.tab()

    await waitFor(() => {
      expect(
        screen.queryByText('Vous devez cocher l’une des options ci-dessus')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Vous devez choisir une date d’envoi')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Vous devez choisir une heure de retrait')
      ).not.toBeInTheDocument()
    })

    userEvent.click(await screen.findByText('Envoi par e-mail'))
    await userEvent.tab()

    await waitFor(() => {
      expect(
        screen.queryByText('Vous devez cocher l’une des options ci-dessus')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Vous devez choisir une date d’envoi')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Vous devez choisir une heure de retrait')
      ).not.toBeInTheDocument()
    })

    userEvent.click(
      await screen.findByText('Retrait sur place (guichet, comptoir ...)')
    )
    await userEvent.tab()

    await waitFor(() => {
      expect(
        screen.queryByText('Vous devez cocher l’une des options ci-dessus')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Vous devez choisir une date d’envoi')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Vous devez choisir une heure de retrait')
      ).toBeInTheDocument()
    })
  })
})
