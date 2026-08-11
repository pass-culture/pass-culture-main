import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/compat'
import * as apiHelpers from '@/apiClient/helpers'
import {
  type BankAccountResponseModel,
  type ManagedVenue,
  VenueState,
} from '@/apiClient/v1'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  defaultBankAccount,
  defaultManagedVenue,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { LinkVenuesDialog } from './LinkVenuesDialog'

const mockUpdateVenuePricingPoint = vi.fn()
const renderLinkVenuesDialog = (
  offererId: number,
  selectedBankAccount: BankAccountResponseModel,
  managedVenues: Array<ManagedVenue>,
  closeDialog: (update?: boolean) => void = vi.fn(),
  updateBankAccountVenuePricingPoint: (
    venueId: number
  ) => void = mockUpdateVenuePricingPoint,
  options: RenderWithProvidersOptions = {}
) => {
  return renderWithProviders(
    <LinkVenuesDialog
      offererId={offererId}
      selectedBankAccount={selectedBankAccount}
      managedVenues={managedVenues}
      closeDialog={closeDialog}
      updateBankAccountVenuePricingPoint={updateBankAccountVenuePricingPoint}
    />,
    options
  )
}

describe('LinkVenueDialog', () => {
  let snackBarsImport: ReturnType<typeof useSnackBar.useSnackBar>

  beforeAll(async () => {
    snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
  })

  it('should select all venues when clicking on select all checkbox', async () => {
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      { ...defaultManagedVenue, id: 2, commonName: 'Lieu 2' },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )

    expect(screen.getByRole('checkbox', { name: 'Lieu 1' })).toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Lieu 2' })).toBeChecked()
  })

  it('should display closed tag for closed venue', () => {
    const managedVenues = [
      {
        ...defaultManagedVenue,
        id: 1,
        commonName: 'Lieu 1',
        state: VenueState.CLOSED,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(screen.getByText('Structure fermée')).toBeInTheDocument()
  })

  it('should display select siret button if venue does not have pricing point', () => {
    const managedVenues = [
      defaultManagedVenue,
      { ...defaultManagedVenue, id: 2, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(
      screen.getAllByRole('button', { name: 'Sélectionner un SIRET' })
    ).toHaveLength(1)
  })

  it('should display pricing point pop-in when clicking select siret button', async () => {
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    const selectSiretButton = screen.getByRole('button', {
      name: 'Sélectionner un SIRET',
    })
    await userEvent.click(selectSiretButton)

    expect(
      screen.getByRole('heading', {
        name: /Sélectionnez un SIRET pour la structure “Mon super lieu”/,
      })
    ).toBeInTheDocument()
  })

  it('should close link venues modal when clicking cancel without changes', async () => {
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
    ]

    renderLinkVenuesDialog(
      1,
      { ...defaultBankAccount, linkedVenues: [] },
      managedVenues,
      closeDialog
    )

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(closeDialog).toHaveBeenCalledTimes(1)
  })

  it('should open discard confirmation on cancel with changes and close on confirm', async () => {
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
    ]

    renderLinkVenuesDialog(
      1,
      { ...defaultBankAccount, linkedVenues: [] },
      managedVenues,
      closeDialog
    )

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 1' }))
    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(
      screen.getByText(
        'Les informations non sauvegardées ne seront pas prises en compte'
      )
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Quitter sans enregistrer' })
    )

    expect(closeDialog).toHaveBeenCalledTimes(1)
  })

  it('should close pricing point pop-in when clicking cancel', async () => {
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Sélectionner un SIRET',
      })
    )

    expect(
      screen.getByRole('heading', {
        name: /Sélectionnez un SIRET pour la structure “Mon super lieu”/,
      })
    ).toBeInTheDocument()

    await userEvent.click(screen.getAllByRole('button', { name: 'Annuler' })[1])

    expect(
      screen.queryByRole('heading', {
        name: /Sélectionnez un SIRET pour la structure “Mon super lieu”/,
      })
    ).not.toBeInTheDocument()
  })

  it('should update venue selection when selecting pricing point', async () => {
    vi.spyOn(api, 'linkVenueToPricingPoint').mockResolvedValue()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, hasPricingPoint: true },
      {
        ...defaultManagedVenue,
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
        'Structure avec SIRET utilisée pour le calcul du barème de remboursement'
      ),
      screen.getByRole('option', { name: 'RAISON SOCIALE - 123456789' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la sélection' })
    )

    expect(mockUpdateVenuePricingPoint).toHaveBeenCalled()
  })

  it('should display error message when attach pricing point fail', async () => {
    vi.spyOn(api, 'linkVenueToPricingPoint').mockRejectedValue({})
    const snackBarError = vi.fn()
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, hasPricingPoint: true, name: 'raison' },
      {
        ...defaultManagedVenue,
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
        'Structure avec SIRET utilisée pour le calcul du barème de remboursement'
      ),
      screen.getByRole('option', { name: 'raison - 123456789' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la sélection' })
    )

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue. Merci de réessayer plus tard'
    )
  })

  it('should display banner if at least one venue has no pricing point', () => {
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, hasPricingPoint: true },
      { ...defaultManagedVenue, id: 2, hasPricingPoint: false },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(
      screen.getByText('Certaines de vos structures n’ont pas de SIRET')
    ).toBeInTheDocument()
  })

  it('should display "Sélectionner un SIRET" button for venue that has no pricing point', () => {
    const managedVenues = [
      {
        ...defaultManagedVenue,
        id: 1,
        hasPricingPoint: false,
        commonName: 'Lieu sans SIRET',
        siret: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(
      screen.getByRole('checkbox', { name: 'Lieu sans SIRET' })
    ).toBeDisabled()

    expect(
      screen.getByRole('button', {
        name: 'Sélectionner un SIRET',
      })
    ).toBeInTheDocument()
  })

  it('should not display "Sélectionner un SIRET" button for venue that has pricing point', () => {
    const managedVenues = [
      {
        ...defaultManagedVenue,
        id: 1,
        hasPricingPoint: true,
        commonName: 'Lieu avec SIRET',
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    expect(
      screen.getByRole('checkbox', { name: 'Lieu avec SIRET' })
    ).toBeEnabled()

    expect(screen.queryByText('Sélectionner un SIRET')).not.toBeInTheDocument()
  })

  it('should not be able to link a venue already attached to another bank account', () => {
    const venueName = 'Mon super lieu'
    const venues = [
      {
        ...defaultManagedVenue,
        name: venueName,
        id: 1,
        hasPricingPoint: true,
        bankAccountId: 2,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, venues)

    expect(screen.getByRole('checkbox', { name: venueName })).toBeDisabled()
  })

  it('should not select venues attached to another bank account when clicking on select all checkbox', async () => {
    const managedVenues = [
      {
        ...defaultManagedVenue,
        id: 1,
        commonName: 'Lieu 1',
        hasPricingPoint: true,
      },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        hasPricingPoint: true,
        bankAccountId: 999,
      },
    ]

    renderLinkVenuesDialog(
      1,
      { ...defaultBankAccount, linkedVenues: [] },
      managedVenues
    )

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )

    expect(screen.getByRole('checkbox', { name: 'Lieu 1' })).toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Lieu 2' })).not.toBeChecked()
  })

  it('should be able to unlink a venue already attached to the same bank account', async () => {
    const venueName = 'Mon super lieu'
    const venues = [
      {
        ...defaultManagedVenue,
        id: 1,
        name: venueName,
        hasPricingPoint: true,
        bankAccountId: 2,
      },
    ]

    const bankAccount = { ...defaultBankAccount, id: 2 }

    renderLinkVenuesDialog(1, bankAccount, venues)

    const checkbox = screen.getByRole('checkbox', { name: venueName })
    expect(checkbox).toBeChecked()
    await userEvent.click(checkbox)
    expect(checkbox).not.toBeChecked()
  })

  it('should close dialog with update on successful form submission', async () => {
    vi.spyOn(api, 'linkVenueToBankAccount').mockResolvedValue()
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues, closeDialog)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(closeDialog).toHaveBeenCalledWith(true)
  })

  it('should close dialog without update when submitting unchanged venues selection', async () => {
    const closeDialog = vi.fn()
    const linkVenueToBankAccountSpy = vi.spyOn(api, 'linkVenueToBankAccount')
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues, closeDialog)

    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(closeDialog).toHaveBeenCalledWith(false)
    expect(linkVenueToBankAccountSpy).not.toHaveBeenCalled()
  })

  it('should call handleCancel from DetailedModal onClose when no confirmation dialog is open', async () => {
    const closeDialog = vi.fn()

    renderLinkVenuesDialog(
      1,
      defaultBankAccount,
      [defaultManagedVenue],
      closeDialog
    )

    const detailedDialog = screen.getByRole('dialog', {
      name: 'Compte bancaire : Mon compte bancaire',
    })

    await userEvent.click(
      within(detailedDialog).getByLabelText('Fermer la boite de dialogue')
    )

    expect(closeDialog).toHaveBeenCalledOnce()
  })

  it('should not call handleCancel from DetailedModal onClose when discard dialog is open', async () => {
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues, closeDialog)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(
      screen.getByText(
        'Les informations non sauvegardées ne seront pas prises en compte'
      )
    ).toBeInTheDocument()

    const detailedDialog = screen.getByRole('dialog', {
      name: 'Compte bancaire : Mon compte bancaire',
    })

    await userEvent.click(
      within(detailedDialog).getByLabelText('Fermer la boite de dialogue')
    )

    expect(closeDialog).not.toHaveBeenCalled()
  })

  it('should close discard dialog on close icon click without closing parent dialog', async () => {
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues, closeDialog)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    const discardDialog = screen.getByRole('dialog', {
      name: 'Les informations non sauvegardées ne seront pas prises en compte',
    })

    await userEvent.click(
      within(discardDialog).getByLabelText('Fermer la boite de dialogue')
    )

    expect(closeDialog).not.toHaveBeenCalled()
  })

  it('should close discard dialog on cancel button click without closing parent dialog', async () => {
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues, closeDialog)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    const discardDialog = screen.getByRole('dialog', {
      name: 'Les informations non sauvegardées ne seront pas prises en compte',
    })

    await userEvent.click(
      within(discardDialog).getByRole('button', { name: 'Annuler' })
    )

    expect(closeDialog).not.toHaveBeenCalled()
  })

  it('should close discard dialog and close parent dialog when clicking "Quitter sans enregistrer"', async () => {
    const closeDialog = vi.fn()
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues, closeDialog)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    const discardDialog = screen.getByRole('dialog', {
      name: 'Les informations non sauvegardées ne seront pas prises en compte',
    })

    await userEvent.click(
      within(discardDialog).getByRole('button', {
        name: 'Quitter sans enregistrer',
      })
    )

    expect(closeDialog).toHaveBeenCalledOnce()
  })

  it('should call serializeApiErrors when linkVenueToBankAccount fails with a 400 error', async () => {
    const error = new ApiError('', 400, 'Bad Request', {
      venuesIds: ['Erreur de validation'],
    })
    vi.spyOn(api, 'linkVenueToBankAccount').mockRejectedValue(error)
    vi.spyOn(apiHelpers, 'serializeApiErrors')
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(apiHelpers.serializeApiErrors).toHaveBeenCalledWith(
      { venuesIds: ['Erreur de validation'] },
      expect.any(Function)
    )
  })

  it('should display the venuesIds error message when linkVenueToBankAccount returns 400', async () => {
    const errorMessage =
      'Une ou plusieurs structures sélectionnées sont déjà rattachées à un autre compte bancaire.'
    vi.spyOn(api, 'linkVenueToBankAccount').mockRejectedValue(
      new ApiError('', 400, 'Bad Request', {
        venuesIds: [errorMessage],
      })
    )

    const managedVenues = [
      defaultManagedVenue,
      {
        ...defaultManagedVenue,
        id: 2,
        hasPricingPoint: true,
        commonName: 'Lieu 2',
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(await screen.findByText(errorMessage)).toBeInTheDocument()
  })

  it('should display error snackbar when linkVenueToBankAccount fails with a non-400 ApiError', async () => {
    vi.spyOn(api, 'linkVenueToBankAccount').mockRejectedValue(
      new ApiError('', 500, 'Internal Server Error', {})
    )
    const snackBarError = vi.fn()
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(snackBarError).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
  })

  it('should display error snackbar when linkVenueToBankAccount fails with a non-400 error', async () => {
    vi.spyOn(api, 'linkVenueToBankAccount').mockRejectedValue(
      new Error('Server error')
    )
    const snackBarError = vi.fn()
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))
    const managedVenues = [
      { ...defaultManagedVenue, id: 1, commonName: 'Lieu 1' },
      {
        ...defaultManagedVenue,
        id: 2,
        commonName: 'Lieu 2',
        bankAccountId: null,
      },
    ]

    renderLinkVenuesDialog(1, defaultBankAccount, managedVenues)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Lieu 2' }))
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(snackBarError).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
  })
})
