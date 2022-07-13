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
import { TICKET_WITHDRAWAL_DEFAULT_VALUES } from '.'
import { WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE } from '..'
import { useFormikContext } from 'formik'

const TicketWithdrawal = (): JSX.Element => {
  const {
    values: { subcategoryId, withdrawalType },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(
    function onSubCategoryChange() {
      if (!WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(subcategoryId)) {
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
            description="avant le début de l'évènement"
            name="withdrawalDelay"
            options={ticketSentDateOptions}
          />
        </FormLayout.Row>
      )}

      {withdrawalType === WITHDRAWAL_TYPE.onPlaceTicket && (
        <FormLayout.Row>
          <Select
            label="Heure de retrait"
            description="avant le début de l'évènement"
            name="withdrawalDelay"
            options={ticketWithdrawalHourOptions}
          />
        </FormLayout.Row>
      )}
    </>
  )
}

export default TicketWithdrawal
