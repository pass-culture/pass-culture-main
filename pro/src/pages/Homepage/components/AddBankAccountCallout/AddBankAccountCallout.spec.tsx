import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AddBankAccountCallout } from '@/pages/Homepage/components/AddBankAccountCallout/AddBankAccountCallout'

const mockLogEvent = vi.fn()

describe('AddBankAccountCallout', () => {
  it('should render the banner with the expected title and link', () => {
    renderWithProviders(<AddBankAccountCallout venue={defaultGetVenue} />)

    expect(
      screen.getByText(
        'Aucun compte bancaire configuré pour percevoir vos remboursements'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Ajouter un compte bancaire' })
    ).toBeInTheDocument()
  })

  it('should log CLICKED_ADD_BANK_ACCOUNT when clicking on add bank account link', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const venue = { ...defaultGetVenue, id: 42 }
    renderWithProviders(<AddBankAccountCallout venue={venue} />, {
      initialRouterEntries: ['/accueil'],
    })

    await userEvent.click(
      screen.getByRole('link', { name: 'Ajouter un compte bancaire' })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT,
      {
        from: '/accueil',
        venueId: 42,
      }
    )
  })
})
