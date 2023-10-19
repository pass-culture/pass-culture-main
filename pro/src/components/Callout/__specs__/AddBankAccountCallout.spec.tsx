import { screen } from '@testing-library/react'
import React from 'react'

import AddBankAccountCallout, {
  AddBankAccountCalloutProps,
} from 'components/Callout/AddBankAccountCallout'
import { defautGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

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
        /Rendez-vous dans l'onglet informations bancaires de votre page Remboursements./
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Ajouter un compte bancaire',
      })
    ).not.toBeInTheDocument()
  })

  describe('With FF enabled', () => {
    const storeOverrides = {
      features: {
        list: [
          { isActive: true, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
        ],
      },
    }

    it.each([
      {
        ...defautGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [],
      },
      {
        ...defautGetOffererResponseModel,
        id: 2,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
        hasValidBankAccount: true,
      },
    ])(
      `should not render the add bank account banner when hasValidBankAccount = $hasValidBankAccount and venuesWithNonFreeOffersWithoutBankAccounts = $venuesWithNonFreeOffersWithoutBankAccounts`,
      async ({
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
          storeOverrides,
        })

        expect(
          screen.queryByText(
            'Ajoutez un compte bancaire pour percevoir vos remboursements'
          )
        ).not.toBeInTheDocument()
      }
    )

    it('should render the add bank account banner if the offerer has no valid bank account and some unlinked venues', async () => {
      props.offerer = {
        ...defautGetOffererResponseModel,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }
      renderWithProviders(<AddBankAccountCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.getByText(
          'Ajoutez un compte bancaire pour percevoir vos remboursements'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Rendez-vous dans l'onglet informations bancaires de votre page Remboursements./
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Ajouter un compte bancaire',
        })
      ).toBeInTheDocument()
    })
  })
})
