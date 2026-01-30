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

describe('LinkVenueCallout', () => {
  const props: BankAccountHasPendingCorrectionCalloutProps = {
    titleOnly: false,
  }
  describe('With FF disabled', () => {
    it('should not render LinkVenueCallout if offerer has no pending corrections on their bank account', () => {
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

    it('should render LinkVenueCallout if offerer has a bank account with pending corrections', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasBankAccountWithPendingCorrections: true,
      }
      renderWithProviders(<BankAccountHasPendingCorrectionCallout {...props} />)

      expect(screen.getByText(/Compte bancaire incomplet/)).toBeInTheDocument()
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
        BankAccountEvents.CLICKED__BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
        {
          from: '/accueil',
          offererId: 1,
        }
      )
    })
  })

  describe('With FF enabled', () => {
    it('should not render LinkVenueCallout if venue has a bank account status valid or pending', () => {
      props.venue = {
        ...defaultGetVenue,
        bankAccountStatus: SimplifiedBankAccountStatus.VALID,
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

    it('should render LinkVenueCallout if venue has a bank account status with pending corrections', () => {
      props.venue = {
        ...defaultGetVenue,
        bankAccountStatus: SimplifiedBankAccountStatus.PENDING_CORRECTIONS,
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
