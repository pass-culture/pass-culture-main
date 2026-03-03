import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import {
  BankAccountApplicationStatus,
  type BankAccountResponseModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  GET_OFFERER_BANKACCOUNTS_AND_ATTACHED_VENUES,
  GET_VENUE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import {
  defaultBankAccount,
  defaultGetOffererResponseModel,
  defaultManagedVenue,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import { Component as BankInformations } from '@/pages/Reimbursements/BankInformations/BankInformations'

const mockMutate = vi.fn()
vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: vi.fn(() => ({
    mutate: mockMutate,
  })),
}))

const defaultBankAccountResponseModel: BankAccountResponseModel = {
  dateCreated: '2020-05-07',
  dsApplicationId: 1,
  id: 1,
  isActive: true,
  label: 'jacob',
  linkedVenues: [
    {
      commonName: 'carefully',
      id: 1,
    },
  ],
  obfuscatedIban: 'XXXX-123',
  status: BankAccountApplicationStatus.ACCEPTE,
}

function renderBankInformations({
  hasValidBankAccount = false,
  hasPendingBankAccount = false,
}: {
  hasValidBankAccount?: boolean
  hasPendingBankAccount?: boolean
} = {}) {
  renderWithProviders(
    <>
      <BankInformations />
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/remboursements/informations-bancaires'],
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: {
          currentOfferer: {
            ...defaultGetOffererResponseModel,
            hasValidBankAccount,
            hasPendingBankAccount,
          },
        },
      },
    }
  )
}

const mockLogEvent = vi.fn()

describe('BankInformations page', () => {
  beforeEach(() => {
    vi.spyOn(api, 'linkVenueToBankAccount').mockResolvedValue()
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      bankAccounts: [defaultBankAccountResponseModel],
      id: 1,
      managedVenues: [
        {
          ...defaultManagedVenue,
          commonName: 'wanted',
        },
      ],
    })
  })

  it('should display the bank account section', async () => {
    renderBankInformations()

    expect(
      await screen.findByRole('button', {
        name: /Modifier/i,
      })
    ).toBeInTheDocument()
  })

  it('should display discard dialog on cancel', async () => {
    const user = userEvent.setup()
    renderBankInformations()

    await user.click(
      await screen.findByRole('button', {
        name: 'Modifier',
      })
    )

    expect(
      await screen.findByText(
        /Sélectionnez les structures dont les offres seront remboursées sur ce compte bancaire/
      )
    ).toBeInTheDocument()

    await user.click(screen.getByText('wanted'))

    await user.click(
      screen.getByRole('button', {
        name: 'Annuler',
      })
    )

    expect(
      screen.queryByText(
        /Les informations non sauvegardées ne seront pas prises en compte/
      )
    ).toBeInTheDocument()
  })

  it('should display unlink venues dialog', async () => {
    const user = userEvent.setup()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderBankInformations()

    await user.click(
      await screen.findByRole('button', {
        name: 'Modifier',
      })
    )

    await user.click(screen.getByText('wanted'))

    await user.click(
      screen.getByRole('button', {
        name: 'Enregistrer',
      })
    )

    expect(
      screen.queryByText(
        /Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire/
      )
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('button', {
        name: 'Confirmer',
      })
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      'HasClickedSaveVenueToBankAccount',
      expect.objectContaining({
        id: 1,
        HasUncheckedVenue: true,
      })
    )
  })

  it('should display the bank account section even without context', async () => {
    renderBankInformations()

    expect(
      await screen.findByRole('button', {
        name: /Ajouter un compte bancaire/i,
      })
    ).toBeInTheDocument()
  })

  it('should display not validated bank account message', async () => {
    renderBankInformations()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByText(
        /Ajoutez au moins un compte bancaire pour percevoir vos remboursements/
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should render message when the user has a valid bank account and no pending one', async () => {
    renderBankInformations({
      hasValidBankAccount: true,
      hasPendingBankAccount: false,
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByText(
        'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l’objet d’un remboursement et d’un justificatif de remboursement distincts.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should render message when has a pending bank account and no valid one', async () => {
    renderBankInformations({ hasPendingBankAccount: true })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByText(
        'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l’objet d’un remboursement et d’un justificatif de remboursement distincts.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should render default page if error on getOffererBankAccountsAndAttachedVenues request', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockRejectedValueOnce({})

    renderBankInformations()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText(
        'Impossible de récupérer les informations relatives à vos comptes bancaires.'
      )
    ).toBeInTheDocument()
  })

  it('should render with default offerer select ', async () => {
    renderBankInformations()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByText('Ajouter un compte bancaire')).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).not.toBeInTheDocument()
  })

  it('should render with default offerer select', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'first offerer',
        }),
        getOffererNameFactory({
          id: 2,
          name: 'second offerer',
        }),
      ],
    })
    renderBankInformations()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByText('Ajouter un compte bancaire')).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should show AddBankInformationsDialog on click add bank account button', async () => {
    const user = userEvent.setup()
    renderBankInformations()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByText(
        'Vous allez être redirigé vers le site demarche.numerique.gouv.fr'
      )
    ).not.toBeInTheDocument()

    await user.click(await screen.findByText('Ajouter un compte bancaire'))

    expect(
      screen.getByText(
        'Vous allez être redirigé vers le site demarche.numerique.gouv.fr'
      )
    ).toBeInTheDocument()

    await user.click(
      await screen.findByRole('button', { name: 'Fermer la fenêtre modale' })
    )

    expect(
      screen.queryByText(
        'Vous allez être redirigé vers le site demarche.numerique.gouv.fr'
      )
    ).not.toBeInTheDocument()
  })

  it('should track add bank account button', async () => {
    const user = userEvent.setup()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderBankInformations()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await user.click(screen.getByText('Ajouter un compte bancaire'))
    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT,
      {
        from: '/remboursements/informations-bancaires',
        offererId: 1,
      }
    )
  })

  it('should update displayed link venue after closing link venue dialog', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'linkVenueToBankAccount').mockResolvedValue()
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [{ ...defaultBankAccount }],
      managedVenues: [{ ...defaultManagedVenue }],
    })

    renderBankInformations({
      hasValidBankAccount: true,
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await user.click(screen.getByRole('button', { name: 'Modifier' }))

    await user.click(screen.getByRole('checkbox', { name: 'Mon super lieu' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))
    await user.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(mockMutate).toHaveBeenNthCalledWith(1, [
      GET_OFFERER_BANKACCOUNTS_AND_ATTACHED_VENUES,
      1,
    ])
  })

  it('should refresh the selected venue in the Redux store after linking a venue to a bank account', async () => {
    const user = userEvent.setup()
    const venue = makeGetVenueResponseModel({ id: 1 })
    const updatedVenue = makeGetVenueResponseModel({
      id: 1,
      bankAccount: {
        id: 1,
        label: 'jacob',
        obfuscatedIban: 'XXXX-123',
        isActive: true,
      },
    })

    vi.spyOn(api, 'linkVenueToBankAccount').mockResolvedValue()
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [{ ...defaultBankAccount }],
      managedVenues: [{ ...defaultManagedVenue }],
    })
    const getVenueSpy = vi
      .spyOn(api, 'getVenue')
      .mockResolvedValue(updatedVenue)

    // Make mockMutate execute the fetcher callback so api.getVenue is actually called
    mockMutate.mockImplementation(
      async (_key: unknown, fetcher?: () => Promise<unknown>) => {
        if (typeof fetcher === 'function') {
          return await fetcher()
        }
        return undefined
      }
    )

    renderWithProviders(
      <>
        <BankInformations />
        <SnackBarContainer />
      </>,
      {
        user: sharedCurrentUserFactory(),
        initialRouterEntries: ['/remboursements/informations-bancaires'],
        storeOverrides: {
          user: {
            currentUser: sharedCurrentUserFactory(),
            selectedVenue: venue,
          },
          offerer: {
            currentOfferer: {
              ...defaultGetOffererResponseModel,
              hasValidBankAccount: true,
            },
          },
        },
      }
    )
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await user.click(screen.getByRole('button', { name: 'Modifier' }))

    await user.click(screen.getByRole('checkbox', { name: 'Mon super lieu' }))
    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))
    await user.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(mockMutate).toHaveBeenCalledWith(
      [GET_VENUE_QUERY_KEY, String(venue.id)],
      expect.any(Function)
    )
    expect(getVenueSpy).toHaveBeenCalledWith(venue.id)
  })
})
