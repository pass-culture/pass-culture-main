import { screen } from '@testing-library/react'

import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import {
  defaultBankAccountResponseModel,
  defaultManagedVenues,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import LinkVenuesDialog from '../LinkVenuesDialog'

const renderLinkVenuesDialog = (
  offererId: number,
  selectedBankAccount: BankAccountResponseModel,
  managedVenues?: Array<ManagedVenues>,
  closeDialog: (update?: boolean) => void = vi.fn()
) => {
  renderWithProviders(
    <LinkVenuesDialog
      offererId={offererId}
      selectedBankAccount={selectedBankAccount}
      managedVenues={managedVenues}
      closeDialog={closeDialog}
    ></LinkVenuesDialog>
  )
}

describe('LinkVenueDialog', () => {
  it('should display select siret button if venue does not have pricing point', () => {
    const managedVenues = [
      defaultManagedVenues,
      { ...defaultManagedVenues, id: 2, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccountResponseModel, managedVenues)

    expect(
      screen.getAllByRole('button', { name: 'Sélectionner un SIRET' }).length
    ).toEqual(1)
  })
})
