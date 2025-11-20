import { useFormContext } from 'react-hook-form'

import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { Select } from '@/ui-kit/form/Select/Select'

import type { IndividualOfferPracticalInfosFormValues } from '../../../commons/types'

const ticketSentDateOptions = [
  {
    label: '24 heures',
    value: (60 * 60 * 24).toString(),
  },
  {
    label: '48 heures',
    value: (60 * 60 * 24 * 2).toString(),
  },
  {
    label: '3 jours',
    value: (60 * 60 * 24 * 3).toString(),
  },
  {
    label: '4 jours',
    value: (60 * 60 * 24 * 4).toString(),
  },
  {
    label: '5 jours',
    value: (60 * 60 * 24 * 5).toString(),
  },
  {
    label: '6 jours',
    value: (60 * 60 * 24 * 6).toString(),
  },
  {
    label: '1 semaine',
    value: (60 * 60 * 24 * 7).toString(),
  },
]

const ticketWithdrawalHourOptions = [
  {
    label: 'À tout moment',
    value: (0).toString(),
  },
  {
    label: '15 minutes',
    value: (60 * 15).toString(),
  },
  {
    label: '30 minutes',
    value: (60 * 30).toString(),
  },
  {
    label: '1 heure',
    value: (60 * 60).toString(),
  },
  {
    label: '2 heures',
    value: (60 * 60 * 2).toString(),
  },
  {
    label: '4 heures',
    value: (60 * 60 * 4).toString(),
  },
  {
    label: '24 heures',
    value: (60 * 60 * 24).toString(),
  },
  {
    label: '48 heures',
    value: (60 * 60 * 48).toString(),
  },
]

function getFirstWithdrawalTypeEnumValue(value: string) {
  switch (value) {
    case WithdrawalTypeEnum.BY_EMAIL:
      return ticketSentDateOptions[0].value

    case WithdrawalTypeEnum.ON_SITE:
      return ticketWithdrawalHourOptions[0].value

    default:
      return null
  }
}

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
          maxCharactersCount={90}
          disabled={isFormDisabled}
          description="Format : email@exemple.com"
          error={form.formState.errors.bookingContact?.message}
          required
        />
      </FormLayout.Row>
    </>
  )
}
