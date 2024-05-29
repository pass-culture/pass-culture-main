import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { AddBankAccountCallout } from 'components/Callout/AddBankAccountCallout'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = vi.fn()

describe('AddBankAccountCallout', () => {
  it(`should not render the add bank account banner when the user has no valid bank account`, () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: false,
      venuesWithNonFreeOffersWithoutBankAccounts: [],
    }
    renderWithProviders(<AddBankAccountCallout offerer={offerer} />)

    expect(
      screen.queryByText(
        'Aucun compte bancaire configuré pour percevoir vos remboursements'
      )
    ).not.toBeInTheDocument()
  })

  it(`should not render the add bank account banner when the user has a valid bank account and venues with non free offers to link`, () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: true,
      venuesWithNonFreeOffersWithoutBankAccounts: [1],
    }
    renderWithProviders(<AddBankAccountCallout offerer={offerer} />)

    expect(
      screen.queryByText(
        'Aucun compte bancaire configuré pour percevoir vos remboursements'
      )
    ).not.toBeInTheDocument()
  })

  it.each([
    {
      ...defaultGetOffererResponseModel,
      id: 3,
      venuesWithNonFreeOffersWithoutBankAccounts: [1],
      hasPendingBankAccount: true,
    },
  ])(
    `should not render the add bank account banner if the offerer has no valid bank account and some unlinked venues but a pending bank account`,
    () => {
      const offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
        hasPendingBankAccount: true,
      }
      renderWithProviders(<AddBankAccountCallout offerer={offerer} />)

      expect(
        screen.queryByText(
          'Aucun compte bancaire configuré pour percevoir vos remboursements'
        )
      ).not.toBeInTheDocument()
    }
  )

  it('should render the add bank account banner if the offerer has no valid bank account and some unlinked venues', () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: false,
      venuesWithNonFreeOffersWithoutBankAccounts: [1],
    }
    renderWithProviders(<AddBankAccountCallout offerer={offerer} />)

    expect(
      screen.getByText(
        'Aucun compte bancaire configuré pour percevoir vos remboursements'
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/Ajouter un compte bancaire/)).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: 'Ajouter un compte bancaire',
      })
    ).toBeInTheDocument()
  })

  it('should log add bank account on click add bank account link', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: false,
      venuesWithNonFreeOffersWithoutBankAccounts: [1],
    }

    renderWithProviders(<AddBankAccountCallout offerer={offerer} />, {
      initialRouterEntries: ['/accueil'],
    })

    await userEvent.click(screen.getByText('Ajouter un compte bancaire'))

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT,
      {
        from: '/accueil',
        offererId: 1,
      }
    )
  })
})
