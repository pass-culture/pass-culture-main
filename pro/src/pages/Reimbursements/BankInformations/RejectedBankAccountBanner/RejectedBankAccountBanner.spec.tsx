import { screen } from '@testing-library/react'

import type {
  DetachedVenueResponseModel,
  RejectedBankAccountResponseModel,
} from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  RejectedBankAccountBanner,
  type RejectedBankAccountBannerProps,
} from './RejectedBankAccountBanner'

const mockOnAddBankAccount = vi.fn()
const mockOnReplaceBankAccount = vi.fn()

const defaultDetachedVenue: DetachedVenueResponseModel = {
  id: 1,
  publicName: 'Structure 1',
}

const defaultRejectedBankAccount: RejectedBankAccountResponseModel = {
  id: 1,
  label: 'Compte 1',
  obfuscatedIban: 'XXXX XXXX XXXX 1234',
  rejectedSettlementLabel: 'VIR1',
  detachedVenues: [defaultDetachedVenue],
}

const defaultProps = {
  rejectedBankAccount: defaultRejectedBankAccount,
  bankAccounts: [],
  onAddBankAccount: mockOnAddBankAccount,
  onReplaceBankAccount: mockOnReplaceBankAccount,
}

function renderRejectedBankAccountBanner({
  rejectedBankAccount,
  bankAccounts,
  onAddBankAccount,
  onReplaceBankAccount,
}: RejectedBankAccountBannerProps = defaultProps) {
  renderWithProviders(
    <RejectedBankAccountBanner
      rejectedBankAccount={rejectedBankAccount}
      bankAccounts={bankAccounts}
      onAddBankAccount={onAddBankAccount}
      onReplaceBankAccount={onReplaceBankAccount}
    />
  )
}

describe('RejectedBankAccountBanner', () => {
  it('should display a correct description', () => {
    renderRejectedBankAccountBanner()

    expect(
      screen.getByText('Le compte bancaire du virement VIR1 a été rejeté')
    ).toBeInTheDocument()

    expect(screen.getByTestId('banner-content')).toHaveTextContent(
      'Le compte bancaire Compte 1 (IBAN **** 1234) a été rejeté lors du virement et supprimé de cette page. Structure 1 en a été détachée.'
    )

    expect(
      screen.getByText(
        /Choisissez un compte de remplacement : cette structure y sera rattachée et un nouveau virement sera émis./
      )
    ).toBeInTheDocument()
  })

  it('should display multiple venues', () => {
    renderRejectedBankAccountBanner({
      ...defaultProps,
      rejectedBankAccount: {
        ...defaultRejectedBankAccount,
        detachedVenues: [
          { id: 1, publicName: 'Structure 1' },
          { id: 2, publicName: 'Structure 2' },
          { id: 3, publicName: 'Structure 3' },
        ],
      },
    })

    expect(screen.getByTestId('banner-content')).toHaveTextContent(
      'Le compte bancaire Compte 1 (IBAN **** 1234) a été rejeté lors du virement et supprimé de cette page. Structure 1, Structure 2 et Structure 3 en ont été détachées.'
    )
  })
})
