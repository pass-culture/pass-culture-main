import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import AddBankAccountCallout, {
  AddBankAccountCalloutProps,
} from 'components/Callout/AddBankAccountCallout'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = vi.fn()

describe('AddBankAccountCallout', () => {
  const props: AddBankAccountCalloutProps = {
    titleOnly: false,
  }
  it('should not render AddBankAccountCallout without WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY FF', () => {
    renderWithProviders(<AddBankAccountCallout {...props} />)

    expect(
      screen.queryByText(
        'Ajoutez un compte bancaire pour percevoir vos remboursements'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        /Rendez-vous dans l’onglet Informations bancaires de votre page Gestion financière./
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Ajouter un compte bancaire',
      })
    ).not.toBeInTheDocument()
  })

  describe('With WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY FF enabled', () => {
    it(`should not render the add bank account banner when the user has no valid bank account`, () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [],
      }
      renderWithProviders(<AddBankAccountCallout {...props} />, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
      })

      expect(
        screen.queryByText(
          'Ajoutez un compte bancaire pour percevoir vos remboursements'
        )
      ).not.toBeInTheDocument()
    })

    it(`should not render the add bank account banner when the user has a valid bank account and venues with non free offers to link`, () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }
      renderWithProviders(<AddBankAccountCallout {...props} />, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
      })

      expect(
        screen.queryByText(
          'Ajoutez un compte bancaire pour percevoir vos remboursements'
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
        props.offerer = {
          ...defaultGetOffererResponseModel,
          hasValidBankAccount: false,
          venuesWithNonFreeOffersWithoutBankAccounts: [1],
          hasPendingBankAccount: true,
        }
        renderWithProviders(<AddBankAccountCallout {...props} />, {
          features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
        })

        expect(
          screen.queryByText(
            'Ajoutez un compte bancaire pour percevoir vos remboursements'
          )
        ).not.toBeInTheDocument()
      }
    )

    it('should render the add bank account banner if the offerer has no valid bank account and some unlinked venues', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }
      renderWithProviders(<AddBankAccountCallout {...props} />, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
      })

      expect(
        screen.getByText(
          'Ajoutez un compte bancaire pour percevoir vos remboursements'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Rendez-vous dans l’onglet Informations bancaires de votre page Gestion financière./
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Ajouter un compte bancaire',
        })
      ).toBeInTheDocument()
    })

    it('should log add bank account on click add bank account link', async () => {
      vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }

      renderWithProviders(<AddBankAccountCallout {...props} />, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
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
})
