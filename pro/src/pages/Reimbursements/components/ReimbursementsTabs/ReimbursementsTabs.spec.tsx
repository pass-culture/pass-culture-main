import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { FinanceEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ReimbursementsTabs } from './ReimbursementsTabs'

const mockLogEvent = vi.fn()
const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

const renderReimbursementsTabs = () =>
  renderWithProviders(
    <ReimbursementsTabs selectedOfferer={defaultGetOffererResponseModel} />
  )

describe('ReimbursementsTabs', () => {
  it('should render ReimbursementsTabs', () => {
    renderReimbursementsTabs()

    expect(screen.getByRole('tab', { name: /Virements/ })).toBeVisible()
    expect(screen.getByRole('tab', { name: /Justificatifs/ })).toBeVisible()
    expect(
      screen.getByRole('tab', { name: /Informations bancaires/ })
    ).toBeVisible()
    expect(
      screen.getByRole('tab', { name: /Chiffre d'affaires/ })
    ).toBeVisible()
  })

  it.each([
    { tabName: /Virements/, event: FinanceEvents.CLICKED_SETTLEMENTS_TAB },
    { tabName: /Justificatifs/, event: FinanceEvents.CLICKED_INVOICES_TAB },
    {
      tabName: /Informations bancaires/,
      event: FinanceEvents.CLICKED_BANK_INFO_TAB,
    },
    { tabName: /Chiffre d'affaires/, event: FinanceEvents.CLICKED_REVENUE_TAB },
  ])(
    'should log an event on tab $tabName click',
    async ({ tabName, event }) => {
      const user = userEvent.setup()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      renderReimbursementsTabs()

      await user.click(screen.getByRole('tab', { name: tabName }))
      expect(mockLogEvent).toHaveBeenCalledExactlyOnceWith(event)
    }
  )
})
