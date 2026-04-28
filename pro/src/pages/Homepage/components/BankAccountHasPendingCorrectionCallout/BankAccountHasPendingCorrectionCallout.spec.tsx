import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { BankAccountHasPendingCorrectionCallout } from './BankAccountHasPendingCorrectionCallout'

const mockLogEvent = vi.fn()

describe('BankAccountHasPendingCorrectionCallout', () => {
  it('should render the banner with the expected title and link', () => {
    renderWithProviders(
      <BankAccountHasPendingCorrectionCallout venue={defaultGetVenue} />
    )

    expect(screen.getByText(/Compte bancaire incomplet/)).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Voir les corrections attendues' })
    ).toHaveAttribute(
      'href',
      '/administration/remboursements/informations-bancaires'
    )
  })

  it('should log CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS when clicking on the pending corrections link', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const venue = { ...defaultGetVenue, id: 42 }
    renderWithProviders(
      <BankAccountHasPendingCorrectionCallout venue={venue} />,
      { initialRouterEntries: ['/accueil'] }
    )

    await userEvent.click(
      screen.getByRole('link', { name: 'Voir les corrections attendues' })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
      {
        from: '/accueil',
        venueId: 42,
      }
    )
  })
})
