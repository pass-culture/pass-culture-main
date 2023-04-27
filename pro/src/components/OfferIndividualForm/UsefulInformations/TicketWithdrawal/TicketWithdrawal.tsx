import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { RadioGroup, Select } from 'ui-kit'

import { IOfferIndividualFormValues } from '../../types'

import {
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from './constants'

export interface ITicketWithdrawalProps {
  readOnlyFields?: string[]
}

const TicketWithdrawal = ({
  readOnlyFields = [],
}: ITicketWithdrawalProps): JSX.Element => {
  const {
    values: { withdrawalType },
    setFieldValue,
    dirty,
  } = useFormikContext<IOfferIndividualFormValues>()

  const getFirstWithdrawalTypeEnumValue = () => {
    if (withdrawalType === WithdrawalTypeEnum.BY_EMAIL) {
      return ticketSentDateOptions[0].value
    }

    if (withdrawalType === WithdrawalTypeEnum.ON_SITE) {
      return ticketWithdrawalHourOptions[0].value
    }

    /* istanbul ignore next: already tested in InformationsScreen.edition.spec.tsx */
    return undefined
  }

  useEffect(
    function onWithdrawalTypeChange() {
      if (dirty) {
        setFieldValue('withdrawalDelay', getFirstWithdrawalTypeEnumValue())
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
          disabled={readOnlyFields.includes('withdrawalType')}
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

export default TicketWithdrawal
