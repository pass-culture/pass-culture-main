import { useForm } from 'react-hook-form'

import type { BankAccountResponseModel } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullMoreIcon from '@/icons/full-more.svg'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './RejectedBankAccountBannerForm.module.scss'

type FormValues = {
  bankAccountId: number
}

export type RejectedBankAccountBannerFormProps = {
  bankAccounts: BankAccountResponseModel[]
  onAddBankAccount: () => void
  onReplaceBankAccount: (bankAccountId: number) => Promise<boolean>
}

export const RejectedBankAccountBannerForm = ({
  bankAccounts,
  onAddBankAccount,
  onReplaceBankAccount,
}: RejectedBankAccountBannerFormProps): JSX.Element => {
  const getBankAccountOptions = () =>
    bankAccounts.map((bankAccount) => ({
      value: bankAccount.id,
      label: `${bankAccount.label} (IBAN **** ${bankAccount.obfuscatedIban.slice(-4)})`,
    }))

  const form = useForm<FormValues>({ mode: 'onSubmit' })

  const onSubmit = async (formValues: FormValues) => {
    await onReplaceBankAccount(formValues.bankAccountId)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FormLayout className={styles['replace-bank-account-form']}>
        <FormLayout.Row inline>
          <Select
            {...form.register('bankAccountId', { valueAsNumber: true })}
            label="Compte bancaire de remplacement"
            options={getBankAccountOptions()}
          />

          <div className={styles['replace-bank-account-row-buttons']}>
            <Button
              label="Remplacer"
              isLoading={form.formState.isSubmitting}
              type="submit"
            />

            <p>ou</p>

            <Button
              icon={fullMoreIcon}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              onClick={onAddBankAccount}
              label="Ajouter un compte bancaire"
            />
          </div>
        </FormLayout.Row>
      </FormLayout>
    </form>
  )
}
