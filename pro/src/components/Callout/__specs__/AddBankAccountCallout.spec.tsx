import { screen } from '@testing-library/react'
import React from 'react'

import AddBankAccountCallout, {
  AddBankAccountCalloutProps,
} from 'components/Callout/AddBankAccountCallout'
import { renderWithProviders } from 'utils/renderWithProviders'

describe('AddBankAccountCallout', () => {
  const props: AddBankAccountCalloutProps = {
    smallCallout: false,
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
        /Rendez-vous dans l'onglet informations bancaires de votre page Remboursements/
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'ajouter un compte bancaire',
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

    it('should render AddBankAccountCallout', () => {
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
          /Rendez-vous dans l'onglet informations bancaires de votre page Remboursements/
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'ajouter un compte bancaire',
        })
      ).toBeInTheDocument()
    })

    it('should render a small AddBankAccountCallout', () => {
      props.smallCallout = true
      renderWithProviders(<AddBankAccountCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.queryByText(
          /Rendez-vous dans l'onglet informations bancaires de votre page Remboursements/
        )
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('link', {
          name: 'ajouter un compte bancaire',
        })
      ).not.toBeInTheDocument()
    })
  })
})
