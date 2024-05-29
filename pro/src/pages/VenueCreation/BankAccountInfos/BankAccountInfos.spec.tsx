import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import { BankAccountResponseModel } from 'apiClient/v1'
import { defaultBankAccount } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BankAccountInfos } from './BankAccountInfos'

const renderBankAccountInfos = (
  bankAccount: BankAccountResponseModel | null = null
) => {
  renderWithProviders(
    <Formik initialValues={{}} onSubmit={() => {}}>
      <BankAccountInfos venueBankAccount={bankAccount} />
    </Formik>
  )
}

describe('BankAccountInfos', () => {
  it('should display bankAccount infos if venue has one', () => {
    const bankAccount = {
      ...defaultBankAccount,
      label: 'CB #1',
      obfuscatedIban: '123456',
    }
    renderBankAccountInfos(bankAccount)

    expect(screen.getByLabelText('Compte bancaire')).toHaveValue(
      'CB #1 - 123456'
    )
  })

  it('should display modification banner if venue has a bank account', () => {
    renderBankAccountInfos(defaultBankAccount)

    expect(
      screen.getByText(
        'Vous souhaitez modifier le compte bancaire rattaché à ce lieu ?'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Gérer les remboursements' })
    ).toHaveAttribute('href', '/remboursements/informations-bancaires')
  })

  it('should display add bank account banner if venue has not a bank account', () => {
    renderBankAccountInfos()

    expect(
      screen.getByText('Aucun compte bancaire n’est rattaché à ce lieu.')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Gérer les remboursements' })
    ).toHaveAttribute('href', '/remboursements/informations-bancaires')
  })
})
