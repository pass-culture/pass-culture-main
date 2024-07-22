import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/form/Select/Select'

import { IndividualOfferFormValues } from '../../types'

import {
  providedTicketWithdrawalTypeRadios,
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from './constants'

export interface TicketWithdrawalProps {
  readOnlyFields?: string[]
}

export const TicketWithdrawal = ({
  readOnlyFields = [],
}: TicketWithdrawalProps): JSX.Element => {
  const {
    values: { withdrawalType },
    setFieldValue,
    dirty,
  } = useFormikContext<IndividualOfferFormValues>()

  const getFirstWithdrawalTypeEnumValue = () => {
    switch (withdrawalType) {
      case WithdrawalTypeEnum.BY_EMAIL:
        return ticketSentDateOptions[0]?.value

      case WithdrawalTypeEnum.ON_SITE:
        return ticketWithdrawalHourOptions[0]?.value

      default:
        return undefined
    }
  }

  useEffect(() => {
    if (dirty) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setFieldValue('withdrawalDelay', getFirstWithdrawalTypeEnumValue())
    }
  }, [withdrawalType])

  return (
    <>
      <FormLayout.Row mdSpaceAfter>
        {/*
          IN_APP withdrawal type is only selectable by offers created by the event API
          Theses offers are not editable by the user
        */}
        <RadioGroup
          group={
            withdrawalType === WithdrawalTypeEnum.IN_APP
              ? providedTicketWithdrawalTypeRadios
              : ticketWithdrawalTypeRadios
          }
          legend="Précisez la façon dont vous distribuerez les billets :"
          name="withdrawalType"
          // when withdrawal Type is IN_APP the field should also be readOnly.
          // I find it better to be explicit about it
          disabled={
            readOnlyFields.includes('withdrawalType') ||
            withdrawalType === WithdrawalTypeEnum.IN_APP
          }
        />
      </FormLayout.Row>

      {withdrawalType === WithdrawalTypeEnum.BY_EMAIL && (
        <FormLayout.Row>
          <Select
            label="Date d’envoi"
            description="avant le début de l’évènement"
            name="withdrawalDelay"
            options={ticketSentDateOptions}
            disabled={readOnlyFields.includes('withdrawalDelay')}
          />
        </FormLayout.Row>
      )}

      {withdrawalType === WithdrawalTypeEnum.ON_SITE && (
        <FormLayout.Row>
          <Select
            label="Heure de retrait"
            description="avant le début de l’évènement"
            name="withdrawalDelay"
            options={ticketWithdrawalHourOptions}
            disabled={readOnlyFields.includes('withdrawalDelay')}
          />
        </FormLayout.Row>
      )}
    </>
  )
}
