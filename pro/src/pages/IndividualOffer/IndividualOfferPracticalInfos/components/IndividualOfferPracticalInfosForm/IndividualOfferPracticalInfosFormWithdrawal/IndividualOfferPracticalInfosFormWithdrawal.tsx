import { useFormContext } from 'react-hook-form'

import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import {
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
} from '@/pages/IndividualOffer/IndividualOfferInformations/commons/constants'
import { getFirstWithdrawalTypeEnumValue } from '@/pages/IndividualOffer/IndividualOfferInformations/components/UsefulInformationForm/UsefulInformationForm'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import type { IndividualOfferPracticalInfosFormValues } from '../../../commons/types'

export type IndividualOfferPracticalInfosFormWithdrawalProps = {
  isFormDisabled: boolean
}

export function IndividualOfferPracticalInfosFormWithdrawal({
  isFormDisabled,
}: IndividualOfferPracticalInfosFormWithdrawalProps) {
  const form = useFormContext<IndividualOfferPracticalInfosFormValues>()

  const withdrawalType = form.watch('withdrawalType')

  const ticketWithdrawalTypeRadios = [
    {
      label: 'Aucun billet n’est nécessaire',
      value: WithdrawalTypeEnum.NO_TICKET,
    },
    {
      label: 'Les billets seront envoyés par email',
      value: WithdrawalTypeEnum.BY_EMAIL,
      collapsed: (
        <Select
          disabled={isFormDisabled}
          {...form.register('withdrawalDelay')}
          label="Date d’envoi - avant le début de l’évènement"
          options={ticketSentDateOptions}
          error={form.formState.errors.withdrawalDelay?.message}
        />
      ),
    },
    {
      label: 'Retrait sur place (guichet, comptoir...)',
      value: WithdrawalTypeEnum.ON_SITE,
      collapsed: (
        <Select
          {...form.register('withdrawalDelay')}
          disabled={isFormDisabled}
          label="Heure de retrait - avant le début de l’évènement"
          options={ticketWithdrawalHourOptions}
        />
      ),
    },
  ]

  const providedTicketWithdrawalTypeRadios = [
    ...ticketWithdrawalTypeRadios,
    {
      label: 'Les billets seront affichés dans l’application',
      value: WithdrawalTypeEnum.IN_APP,
    },
  ]

  return (
    <>
      <FormLayout.Row mdSpaceAfter>
        <RadioButtonGroup
          variant="detailed"
          name="withdrawalType"
          disabled={isFormDisabled}
          checkedOption={withdrawalType || undefined}
          error={form.formState.errors.withdrawalType?.message}
          options={
            withdrawalType === WithdrawalTypeEnum.IN_APP
              ? providedTicketWithdrawalTypeRadios
              : ticketWithdrawalTypeRadios
          }
          label="Précisez la façon dont vous distribuerez les billets&nbsp;:"
          onChange={(e) => {
            form.setValue(
              'withdrawalType',
              e.target.value as WithdrawalTypeEnum,
              { shouldDirty: true }
            )
            form.setValue(
              'withdrawalDelay',
              getFirstWithdrawalTypeEnumValue(e.target.value)
            )
          }}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          {...form.register('bookingContact')}
          label="Email de contact communiqué aux bénéficiaires"
          maxLength={90}
          disabled={isFormDisabled}
          description="Format : email@exemple.com"
          error={form.formState.errors.bookingContact?.message}
          required
        />
      </FormLayout.Row>
    </>
  )
}
