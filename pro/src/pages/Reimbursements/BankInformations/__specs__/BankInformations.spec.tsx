import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Outlet, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import { BankInformations } from 'pages/Reimbursements/BankInformations/BankInformations'
import {
  defaultBankAccount,
  defaultGetOffererResponseModel,
  defaultManagedVenues,
  getOffererNameFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

const renderBankInformations = (offerer: GetOffererResponseModel | null) => {
  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/remboursements/informations-bancaires"
          element={
            <Outlet
              context={{
                selectedOfferer: {
                  ...defaultGetOffererResponseModel,
                  ...offerer,
                },
                setSelectedOfferer: function () {},
              }}
            />
          }
        >
          <Route index element={<BankInformations />} />
        </Route>
      </Routes>
      <Notification />
    </>,
    {
      initialRouterEntries: ['/remboursements/informations-bancaires'],
    }
  )
}

const mockLogEvent = vi.fn()

describe('BankInformations page', () => {
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: false,
    }

    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [],
      managedVenues: [],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
  })

  it('should display not validated bank account message', async () => {
    renderBankInformations({
      ...offerer,
      hasValidBankAccount: false,
      hasPendingBankAccount: false,
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.getByText(
        /Ajoutez au moins un compte bancaire pour percevoir vos remboursements/
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('En savoir plus')).toBeInTheDocument()
  })

  it('should render message when the user has a valid bank account and no pending one', async () => {
    renderBankInformations({
      ...offerer,
      hasValidBankAccount: true,
      hasPendingBankAccount: false,
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
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
    expect(screen.getByText('En savoir plus')).toBeInTheDocument()
  })

  it('should render message when has a pending bank account and no valid one', async () => {
    renderBankInformations({ ...offerer, hasPendingBankAccount: true })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
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
    expect(screen.getByText('En savoir plus')).toBeInTheDocument()
  })

  it('should render default page if error on getOffererBankAccountsAndAttachedVenues request', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockRejectedValueOnce({})

    renderBankInformations(offerer)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Impossible de récupérer les informations relatives à vos comptes bancaires.'
      )
    ).toBeInTheDocument()
  })

  it('should render with default offerer select ', async () => {
    renderBankInformations(offerer)
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
    renderBankInformations(offerer)
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
    renderBankInformations(offerer)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).not.toBeInTheDocument()

    await userEvent.click(await screen.findByText('Ajouter un compte bancaire'))

    expect(
      screen.getByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).toBeInTheDocument()

    await userEvent.click(
      await screen.findByRole('button', { name: 'Fermer la modale' })
    )

    expect(
      screen.queryByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).not.toBeInTheDocument()
  })

  it('should track add bank account button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderBankInformations(offerer)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await userEvent.click(screen.getByText('Ajouter un compte bancaire'))
    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT,
      {
        from: '/remboursements/informations-bancaires',
        offererId: 1,
      }
    )
  })

  it('should update displayed link venue after closing link venue dialog', async () => {
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [{ ...defaultBankAccount }],
      managedVenues: [{ ...defaultManagedVenues }],
    })

    renderBankInformations({
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: true,
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await userEvent.click(screen.getByRole('button', { name: 'Modifier' }))

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Mon super lieu' })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))
    await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(api.getOfferer).toHaveBeenCalledWith(1)
  })
})
