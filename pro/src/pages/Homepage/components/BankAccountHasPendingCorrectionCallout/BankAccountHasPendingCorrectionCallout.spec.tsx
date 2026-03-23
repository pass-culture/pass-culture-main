import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { SimplifiedBankAccountStatus } from '@/apiClient/v1/models/SimplifiedBankAccountStatus'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  BankAccountHasPendingCorrectionCallout,
  type BankAccountHasPendingCorrectionCalloutProps,
} from './BankAccountHasPendingCorrectionCallout'

const mockLogEvent = vi.fn()

describe('BankAccountHasPendingCorrectionCallout', () => {
  const props: BankAccountHasPendingCorrectionCalloutProps = {
    titleOnly: false,
  }
  describe('With FF disabled', () => {
    it('should not render BankAccountHasPendingCorrectionCallout if offerer has no pending corrections on their bank account', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasBankAccountWithPendingCorrections: false,
      }

      renderWithProviders(<BankAccountHasPendingCorrectionCallout {...props} />)

      expect(
        screen.queryByText(/Compte bancaire incomplet/)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('link', {
          name: 'Voir les corrections attendues',
        })
      ).not.toBeInTheDocument()
    })

    it('should not render BankAccountHasPendingCorrectionCallout if offerer has a bank account with pending corrections and no non free offers', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasBankAccountWithPendingCorrections: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [],
      }
      renderWithProviders(<BankAccountHasPendingCorrectionCallout {...props} />)

      expect(
        screen.queryByText(/Compte bancaire incomplet/)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('link', {
          name: 'Voir les corrections attendues',
        })
      ).not.toBeInTheDocument()
    })

    it('should render BankAccountHasPendingCorrectionCallout if offerer has a bank account with pending corrections and some non free offers', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasBankAccountWithPendingCorrections: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }
      renderWithProviders(<BankAccountHasPendingCorrectionCallout {...props} />)

      expect(
        screen.queryByText(/Compte bancaire incomplet/)
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Voir les corrections attendues',
        })
      ).toBeInTheDocument()
    })

    it('should log add venue bank to account', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasBankAccountWithPendingCorrections: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }

      renderWithProviders(
        <BankAccountHasPendingCorrectionCallout {...props} />,
        {
          initialRouterEntries: ['/accueil'],
        }
      )

      await userEvent.click(
        screen.getByRole('link', {
          name: 'Voir les corrections attendues',
        })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        BankAccountEvents.CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
        {
          from: '/accueil',
          offererId: 1,
        }
      )
    })
  })

  describe('With FF enabled', () => {
    it('should not render BankAccountHasPendingCorrectionCallout if venue has a bank account status valid or pending and non free offers', () => {
      props.venue = {
        ...defaultGetVenue,
        bankAccountStatus: SimplifiedBankAccountStatus.VALID,
        hasNonFreeOffers: true,
      }
      renderWithProviders(
        <BankAccountHasPendingCorrectionCallout {...props} />,
        {
          features: ['WIP_SWITCH_VENUE'],
        }
      )

      expect(
        screen.queryByText(/Compte bancaire incomplet/)
      ).not.toBeInTheDocument()
    })

    it('should not render BankAccountHasPendingCorrectionCallout if venue has a pending corrections bank account and no non free offers', () => {
      props.venue = {
        ...defaultGetVenue,
        bankAccountStatus: SimplifiedBankAccountStatus.VALID,
        hasNonFreeOffers: false,
      }
      renderWithProviders(
        <BankAccountHasPendingCorrectionCallout {...props} />,
        {
          features: ['WIP_SWITCH_VENUE'],
        }
      )

      expect(
        screen.queryByText(/Compte bancaire incomplet/)
      ).not.toBeInTheDocument()
    })

    it('should render BankAccountHasPendingCorrectionCallout if venue has a bank account status with pending corrections and non free offers', () => {
      props.venue = {
        ...defaultGetVenue,
        bankAccountStatus: SimplifiedBankAccountStatus.PENDING_CORRECTIONS,
        hasNonFreeOffers: true,
      }
      renderWithProviders(
        <BankAccountHasPendingCorrectionCallout {...props} />,
        {
          features: ['WIP_SWITCH_VENUE'],
        }
      )

      expect(screen.getByText(/Compte bancaire incomplet/)).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Voir les corrections attendues',
        })
      ).toBeInTheDocument()
    })
  })
})
