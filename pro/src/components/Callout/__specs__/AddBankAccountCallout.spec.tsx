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
  it('should not render AddBankAccountCallout without FF', () => {
    renderWithProviders(<AddBankAccountCallout {...props} />)

    expect(
      screen.queryByText(
        'Ajoutez un compte bancaire pour percevoir vos remboursements'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        /Rendez-vous dans l’onglet informations bancaires de votre page Gestion financière./
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Ajouter un compte bancaire',
      })
    ).not.toBeInTheDocument()
  })

  describe('With FF enabled', () => {
    it.each([
      {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [],
      },
      {
        ...defaultGetOffererResponseModel,
        id: 2,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
        hasValidBankAccount: true,
      },
    ])(
      `should not render the add bank account banner when hasValidBankAccount = $hasValidBankAccount and venuesWithNonFreeOffersWithoutBankAccounts = $venuesWithNonFreeOffersWithoutBankAccounts`,
      ({
        hasValidBankAccount,
        venuesWithNonFreeOffersWithoutBankAccounts,
        ...rest
      }) => {
        props.offerer = {
          hasValidBankAccount: hasValidBankAccount,
          venuesWithNonFreeOffersWithoutBankAccounts:
            venuesWithNonFreeOffersWithoutBankAccounts,
          ...rest,
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
          /Rendez-vous dans l’onglet informations bancaires de votre page Gestion financière./
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
