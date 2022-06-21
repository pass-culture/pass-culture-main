import { RadioGroup, Select } from 'ui-kit'
import React, { useEffect } from 'react'
import {
  TICKETWITHDRAWAL,
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from './constants'

import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from '../../types'
import { IOfferSubCategory } from 'core/Offers/types'
import { TICKET_WITHDRAWAL_DEFAULT_VALUES } from '.'
import { useFormikContext } from 'formik'

export interface ITicketWithdrawalProps {
  subCategories: IOfferSubCategory[]
}

const TicketWithdrawal = ({
  subCategories,
}: ITicketWithdrawalProps): JSX.Element => {
  const {
    values: { subcategoryId, ticketWithdrawal },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(
    function onSubCategoryChange() {
      const subCategory = subCategories.find(s => s.id === subcategoryId)
      if (!subCategory?.isEvent) {
        setFieldValue(
          'ticketWithdrawal',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['ticketWithdrawal']
        )
        setFieldValue(
          'ticketSentDate',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['ticketSentDate']
        )
        setFieldValue(
          'ticketWithdrawalHour',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['ticketWithdrawalHour']
        )
      }
    },
    [subcategoryId]
  )

  useEffect(
    function onTicketWithdrawalChange() {
      if (ticketWithdrawal !== TICKETWITHDRAWAL.emailTicket) {
        setFieldValue(
          'ticketSentDate',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['ticketSentDate']
        )
      } else if (ticketWithdrawal !== TICKETWITHDRAWAL.onPlaceTicket) {
        setFieldValue(
          'ticketWithdrawalHour',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['ticketWithdrawalHour']
        )
      }
    },
    [ticketWithdrawal]
  )

  return (
    <>
      <FormLayout.Row>
        <RadioGroup
          group={ticketWithdrawalTypeRadios}
          legend="Comment les billets, places seront-ils transmis ?"
          name="ticketWithdrawal"
        />
      </FormLayout.Row>

      {ticketWithdrawal === TICKETWITHDRAWAL.emailTicket && (
        <FormLayout.Row>
          <Select
            label="Date d’envoi"
            description="avant le début de l'événement"
            name="ticketSentDate"
            options={ticketSentDateOptions}
          />
        </FormLayout.Row>
      )}

      {ticketWithdrawal === TICKETWITHDRAWAL.onPlaceTicket && (
        <FormLayout.Row>
          <Select
            label="Heure de retrait"
            description="avant le début de l'événement"
            name="ticketWithdrawalHour"
            options={ticketWithdrawalHourOptions}
          />
        </FormLayout.Row>
      )}
    </>
  )
}

export default TicketWithdrawal
