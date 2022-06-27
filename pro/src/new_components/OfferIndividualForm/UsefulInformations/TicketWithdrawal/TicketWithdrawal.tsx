import { RadioGroup, Select } from 'ui-kit'
import React, { useEffect } from 'react'
import {
  WITHDRAWAL_TYPE,
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
    values: { subcategoryId, withdrawalType },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(
    function onSubCategoryChange() {
      const subCategory = subCategories.find(s => s.id === subcategoryId)
      if (!subCategory?.isEvent) {
        setFieldValue(
          'withdrawalType',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['withdrawalType']
        )
        setFieldValue(
          'withdrawalDelay',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['withdrawalDelay']
        )
      }
    },
    [subcategoryId]
  )

  useEffect(
    function onWithdrawalTypeChange() {
      if (withdrawalType !== WITHDRAWAL_TYPE.emailTicket) {
        setFieldValue(
          'withdrawalDelay',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['withdrawalDelay']
        )
      } else if (withdrawalType !== WITHDRAWAL_TYPE.onPlaceTicket) {
        setFieldValue(
          'withdrawalDelay',
          TICKET_WITHDRAWAL_DEFAULT_VALUES['withdrawalDelay']
        )
      }
    },
    [withdrawalType]
  )

  return (
    <>
      <FormLayout.Row>
        <RadioGroup
          group={ticketWithdrawalTypeRadios}
          legend="Comment les billets, places seront-ils transmis ?"
          name="withdrawalType"
        />
      </FormLayout.Row>

      {withdrawalType === WITHDRAWAL_TYPE.emailTicket && (
        <FormLayout.Row>
          <Select
            label="Date d’envoi"
            description="avant le début de l'événement"
            name="withdrawalDelay"
            options={ticketSentDateOptions}
          />
        </FormLayout.Row>
      )}

      {withdrawalType === WITHDRAWAL_TYPE.onPlaceTicket && (
        <FormLayout.Row>
          <Select
            label="Heure de retrait"
            description="avant le début de l'événement"
            name="withdrawalDelay"
            options={ticketWithdrawalHourOptions}
          />
        </FormLayout.Row>
      )}
    </>
  )
}

export default TicketWithdrawal
