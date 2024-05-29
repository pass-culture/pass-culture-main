import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { BankAccountApplicationStatus } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { LinkVenuesDialog } from 'pages/Reimbursements/BankInformations/LinkVenuesDialog'
import { defaultManagedVenues } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

vi.mock('apiClient/api', () => ({
  api: {
    linkVenueToBankAccount: vi.fn(),
  },
}))

const mockClose = vi.fn()
const mockLogEvent = vi.fn()

const renderLinkVenuesDialog = () => {
  renderWithProviders(
    <>
      <LinkVenuesDialog
        closeDialog={mockClose}
        managedVenues={[
          {
            ...defaultManagedVenues,
            commonName: 'Lieu 1',
            id: 1,
          },
          {
            ...defaultManagedVenues,
            commonName: 'Lieu 2',
            id: 2,
          },
        ]}
        offererId={1}
        selectedBankAccount={{
          bic: '04d374fc-8338-45c2-a1e7-3a221991fda9',
          dateCreated: '1995-04-07',
          dsApplicationId: 11,
          id: 6877,
          isActive: true,
          label:
            'Pizza mattress searches wellness entirely transition azerbaijan, quit tournament.',
          linkedVenues: [
            {
              commonName: 'Lieu 1',
              id: 1,
            },
          ],
          obfuscatedIban: 'xxxx-xxxxx-xxxx-xxxx-3a221991fda9',
          status: BankAccountApplicationStatus.ACCEPTE,
        }}
        updateBankAccountVenuePricingPoint={vi.fn()}
      />
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
    }
  )
}

describe('LinkVenueDialog', () => {
  beforeEach(() => {
    vi.spyOn(api, 'linkVenueToBankAccount').mockResolvedValue()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should display the dialog', () => {
    renderLinkVenuesDialog()

    expect(
      screen.getByText(
        /Sélectionnez les lieux dont les offres seront remboursées sur ce compte bancaire/
      )
    ).toBeInTheDocument()

    expect(screen.getByText(/1 lieu sélectionné/)).toBeInTheDocument()

    expect(screen.getByLabelText('Lieu 1')).toBeChecked()
    expect(screen.getByLabelText('Lieu 2')).not.toBeChecked()
  })

  it('should be able to submit the form but only close the modal if no changes were made', async () => {
    renderLinkVenuesDialog()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Enregistrer',
      })
    )

    expect(api.linkVenueToBankAccount).not.toHaveBeenCalled()

    expect(
      screen.queryByText(/Vos modifications ont bien été prises en compte/)
    ).not.toBeInTheDocument()

    expect(mockLogEvent).not.toHaveBeenCalled()
  })

  it('should be able to submit the form', async () => {
    renderLinkVenuesDialog()

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: 'Lieu 2',
      })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Enregistrer',
      })
    )

    expect(api.linkVenueToBankAccount).toHaveBeenCalledWith(1, 6877, {
      venues_ids: [1, 2],
    })

    expect(
      await screen.findByText(/Vos modifications ont bien été prises en compte/)
    ).toBeInTheDocument()

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      'HasClickedSaveVenueToBankAccount',
      expect.objectContaining({
        id: 1,
        HasUncheckedVenue: false,
      })
    )
  })

  it('should handle update failure', async () => {
    vi.spyOn(api, 'linkVenueToBankAccount').mockRejectedValueOnce({})

    renderLinkVenuesDialog()

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: 'Lieu 2',
      })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Enregistrer',
      })
    )

    expect(
      await screen.findByText(
        /Un erreur est survenue. Vos modifications n’ont pas été prises en compte/
      )
    ).toBeInTheDocument()
  })

  it('should close the dialog on cancel click', async () => {
    renderLinkVenuesDialog()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Annuler',
      })
    )

    expect(mockClose).toHaveBeenCalled()
  })

  it('should show the discard dialog on cancel click', async () => {
    renderLinkVenuesDialog()

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: 'Lieu 2',
      })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Annuler',
      })
    )

    expect(
      screen.getByText(
        /Les informations non sauvegardées ne seront pas prises en compte/
      )
    ).toBeInTheDocument()
  })
})
