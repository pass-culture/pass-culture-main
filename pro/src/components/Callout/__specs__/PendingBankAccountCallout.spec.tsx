import { screen } from '@testing-library/react'
import React from 'react'

import PendingBankAccountCallout, {
  PendingBankAccountCalloutProps,
} from 'components/Callout/PendingBankAccountCallout'
import { defautGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

describe('PendingBankAccountCallout', () => {
  const props: PendingBankAccountCalloutProps = {
    titleOnly: false,
  }
  it('should not render PendingBankAccountCallout without FF', () => {
    renderWithProviders(<PendingBankAccountCallout {...props} />)

    expect(
      screen.queryByText(
        /Compte bancaire en cours de validation par nos services/
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Suivre mon dossier de compte bancaire',
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

    it('should not render the pending bank account banner if the offerer has no pending bank account', async () => {
      props.offerer = {
        ...defautGetOffererResponseModel,
        hasPendingBankAccount: false,
      }
      renderWithProviders(<PendingBankAccountCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.queryByText(
          /Compte bancaire en cours de validation par nos services/
        )
      ).not.toBeInTheDocument()
    })

    it('should render PendingBankAccountCallout if the offerer has a pending bank account', () => {
      props.offerer = {
        ...defautGetOffererResponseModel,
        hasPendingBankAccount: true,
      }
      renderWithProviders(<PendingBankAccountCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.getByText(
          /Compte bancaire en cours de validation par nos services/
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Suivre mon dossier de compte bancaire',
        })
      ).toBeInTheDocument()
    })
  })
})
