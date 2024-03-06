import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { BankAccountResponseModel, ManagedVenues } from 'apiClient/v1'
import * as useNotification from 'hooks/useNotification'
import {
  defaultManagedVenues,
  defaultBankAccount,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import LinkVenuesDialog from '../LinkVenuesDialog'

const mockUpdateVenuePricingPoint = vi.fn()
const renderLinkVenuesDialog = (
  offererId: number,
  selectedBankAccount: BankAccountResponseModel,
  managedVenues: Array<ManagedVenues>,
  closeDialog: (update?: boolean) => void = vi.fn(),
  updateBankAccountVenuePricingPoint: (
    venueId: number
  ) => void = mockUpdateVenuePricingPoint
) => {
  renderWithProviders(
    <LinkVenuesDialog
      offererId={offererId}
      selectedBankAccount={selectedBankAccount}
      managedVenues={managedVenues}
      closeDialog={closeDialog}
      updateBankAccountVenuePricingPoint={updateBankAccountVenuePricingPoint}
    />
  )
}

describe('LinkVenueDialog', () => {
  it('should select all venues when clicking on select all checkbox', async () => {
    const managedVenues = [
      { ...defaultManagedVenues, id: 1, commonName: 'Lieu 1' },
      { ...defaultManagedVenues, id: 2, commonName: 'Lieu 2' },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )
    expect(screen.getByRole('checkbox', { name: 'Lieu 1' })).toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Lieu 2' })).toBeChecked()
  })

  it('should display select siret button if venue does not have pricing point', () => {
    const managedVenues = [
      defaultManagedVenues,
      { ...defaultManagedVenues, id: 2, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(
      screen.getAllByRole('button', { name: 'Sélectionner un SIRET' }).length
    ).toEqual(1)
  })

  it('should display pricing point pop-in when clicking select siret button', async () => {
    const managedVenues = [
      { ...defaultManagedVenues, id: 1, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    const selectSiretButton = screen.getByRole('button', {
      name: 'Sélectionner un SIRET',
    })
    await userEvent.click(selectSiretButton)

    expect(
      screen.getByRole('heading', {
        name: /Sélectionnez un SIRET pour le lieu “Mon super lieu”/,
      })
    ).toBeInTheDocument()
  })

  it('should update venue selection when selecting pricing point', async () => {
    vi.spyOn(api, 'linkVenueToPricingPoint').mockResolvedValue()
    const managedVenues = [
      { ...defaultManagedVenues, id: 1, hasPricingPoint: true },
      {
        ...defaultManagedVenues,
        id: 2,
        commonName: 'Lieu sans siret',
        hasPricingPoint: false,
        siret: '',
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    const venueWithoutSiretCheckBox = screen.getByRole('checkbox', {
      name: 'Lieu sans siret',
    })
    expect(venueWithoutSiretCheckBox).toBeDisabled()

    const selectSiretButton = screen.getByRole('button', {
      name: 'Sélectionner un SIRET',
    })
    await userEvent.click(selectSiretButton)
    await userEvent.selectOptions(
      screen.getByLabelText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      ),
      screen.getByRole('option', { name: 'Mon super lieu - 123456789' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la sélection' })
    )

    expect(mockUpdateVenuePricingPoint).toHaveBeenCalled()
  })

  it('should display error message when attach pricing point fail', async () => {
    vi.spyOn(api, 'linkVenueToPricingPoint').mockRejectedValue({})
    const mockNotifyError = vi.fn()

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.default>
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
    }))
    const managedVenues = [
      { ...defaultManagedVenues, id: 1, hasPricingPoint: true },
      {
        ...defaultManagedVenues,
        id: 2,
        commonName: 'Lieu sans siret',
        hasPricingPoint: false,
        siret: '',
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Sélectionner un SIRET',
      })
    )
    await userEvent.selectOptions(
      screen.getByLabelText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      ),
      screen.getByRole('option', { name: 'Mon super lieu - 123456789' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la sélection' })
    )

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Une erreur est survenue. Merci de réessayer plus tard'
    )
  })
  it('should display banner if at least one venue has no pricing point', () => {
    const managedVenues = [
      { ...defaultManagedVenues, id: 1, hasPricingPoint: true },
      { ...defaultManagedVenues, id: 2, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(
      screen.getByText('Certains de vos lieux n’ont pas de SIRET')
    ).toBeInTheDocument()
  })
})
