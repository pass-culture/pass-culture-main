import '@testing-library/jest-dom'

import * as yup from 'yup'

import { UsefulInformations, validationSchema } from '..'
import { render, screen } from '@testing-library/react'

import { CATEGORY_STATUS } from 'core/Offers'
import { Formik } from 'formik'
import { IUsefulInformationsProps } from '../UsefulInformations'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'

interface IInitialValues {
  offererId: string
  venueId: string
  subcategoryId: string
  withdrawalDetails: string
  ticketWithdrawal: string
  ticketSentDate: string
  ticketWithdrawalHour: string
}

const renderUsefulInformations = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IInitialValues
  onSubmit: () => void
  props: IUsefulInformationsProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <UsefulInformations {...props} />
    </Formik>
  )
}

describe('OfferIndividual section: UsefulInformations', () => {
  let initialValues: IInitialValues
  let props: IUsefulInformationsProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    const offererNames: TOffererName[] = [
      {
        id: 'AA',
        name: 'Offerer AA',
      },
    ]

    const venueList: TOfferIndividualVenue[] = [
      {
        id: 'AAAA',
        name: 'Venue AAAA',
        managingOffererId: 'AA',
        isVirtual: false,
      },
    ]
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
      offererNames,
      venueList,
      subCategories,
      isUserAdmin: false,
    }
  })

  it('should render the component', async () => {
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    expect(
      await screen.findByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText('Rayonnement national')
    ).not.toBeInTheDocument()
  })

  it('should contain isNational when user is admin', async () => {
    props.isUserAdmin = true
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    await screen.findByRole('heading', { name: 'Informations pratiques' })
    expect(screen.getByLabelText('Rayonnement national')).toBeInTheDocument()
  })

  it('should contain withdrawal ticket informations when subcategory is an event', async () => {
    initialValues.subcategoryId = 'A-A'
    initialValues = {
      ...initialValues,
    }
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      await screen.getByText(
        'Comment les billets, places seront-ils transmis ?'
      )
    ).toBeInTheDocument()
  })

  it('should not contain withdrawal ticket informations when subcategory is not an event', async () => {
    initialValues.subcategoryId = 'B-A'
    initialValues = {
      ...initialValues,
    }
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(
      await screen.queryByText(
        'Comment les billets, places seront-ils transmis ?'
      )
    ).not.toBeInTheDocument()
  })
})
