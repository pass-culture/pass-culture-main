import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { IndividualOfferPracticalInfosFormValues } from '../../../commons/types'
import {
  IndividualOfferPracticalInfosFormWithdrawal,
  type IndividualOfferPracticalInfosFormWithdrawalProps,
} from './IndividualOfferPracticalInfosFormWithdrawal'

function renderIndividualOfferPracticalInfosFormWithdrawal(
  props?: Partial<IndividualOfferPracticalInfosFormWithdrawalProps>
) {
  function IndividualOfferPracticalInfosFormWithdrawalWrapper() {
    const form = useForm<IndividualOfferPracticalInfosFormValues>({
      defaultValues: {
        withdrawalType: WithdrawalTypeEnum.NO_TICKET,
      },
    })
    return (
      <FormProvider {...form}>
        <IndividualOfferPracticalInfosFormWithdrawal
          isFormDisabled={false}
          {...props}
        />
      </FormProvider>
    )
  }
  renderWithProviders(<IndividualOfferPracticalInfosFormWithdrawalWrapper />)
}

describe('IndividualOfferPracticalInfosFormWithdrawal', () => {
  it('should display the withdrawal delay selects based on the selected withdrawal type', async () => {
    renderIndividualOfferPracticalInfosFormWithdrawal()

    const withdrawalGroup = screen.getByRole('group', {
      name: /Précisez la façon dont vous distribuerez les billets/,
    })

    expect(withdrawalGroup).toBeInTheDocument()
    expect(
      screen.queryByRole('combobox', {
        name: 'Date d’envoi - avant le début de l’évènement',
      })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('combobox', {
        name: 'Heure de retrait - avant le début de l’évènement',
      })
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Les billets seront envoyés par email',
      })
    )

    expect(
      screen.getByRole('combobox', {
        name: 'Date d’envoi - avant le début de l’évènement',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Retrait sur place (guichet, comptoir...)',
      })
    )

    expect(
      screen.getByRole('combobox', {
        name: 'Heure de retrait - avant le début de l’évènement',
      })
    ).toBeInTheDocument()
  })
})
