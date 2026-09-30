import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import type { BankAccountResponseModel } from '@/apiClient/v1'
import { defaultBankAccount } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  RejectedBankAccountBannerForm,
  type RejectedBankAccountBannerFormProps,
} from './RejectedBankAccountBannerForm'

const mockOnAddBankAccount = vi.fn()
const mockOnReplaceBankAccount = vi.fn()

const defaultProps: RejectedBankAccountBannerFormProps = {
  bankAccounts: [],
  onAddBankAccount: mockOnAddBankAccount,
  onReplaceBankAccount: mockOnReplaceBankAccount,
}

function renderRejectedBankAccountBannerForm({
  bankAccounts,
  onAddBankAccount,
  onReplaceBankAccount,
}: RejectedBankAccountBannerFormProps = defaultProps) {
  renderWithProviders(
    <RejectedBankAccountBannerForm
      bankAccounts={bankAccounts}
      onAddBankAccount={onAddBankAccount}
      onReplaceBankAccount={onReplaceBankAccount}
    />
  )
}

describe('RejectedBankAccountBannerForm', () => {
  it('should call onReplaceBankAccount on bank account select', async () => {
    const user = userEvent.setup()

    const bankAccounts: BankAccountResponseModel[] = [
      {
        ...defaultBankAccount,
        id: 1,
        label: 'Compte 1',
        obfuscatedIban: 'XXXX XXXX XXXX 1234',
      },
      {
        ...defaultBankAccount,
        id: 2,
        label: 'Compte 2',
        obfuscatedIban: 'XXXX XXXX XXXX 5678',
      },
    ]
    renderRejectedBankAccountBannerForm({ ...defaultProps, bankAccounts })

    const selectBankAccountButton = screen.getByLabelText(
      'Compte bancaire de remplacement'
    )
    await user.selectOptions(
      selectBankAccountButton,
      screen.getByRole('option', { name: 'Compte 1 (IBAN **** 1234)' })
    )

    await user.click(screen.getByRole('button', { name: 'Remplacer' }))

    expect(mockOnReplaceBankAccount).toHaveBeenCalledExactlyOnceWith(1)
  })

  it('should call onAddBankAccount on click add bank account button', async () => {
    const user = userEvent.setup()
    renderRejectedBankAccountBannerForm()

    await user.click(await screen.findByText('Ajouter un compte bancaire'))

    expect(mockOnAddBankAccount).toHaveBeenCalledOnce()
  })
})
