import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { FinanceEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ReimbursementsTabs } from './ReimbursementsTabs'

const mockLogEvent = vi.fn()

const renderReimbursementsTabs = (isSettlementEnable: boolean) =>
  renderWithProviders(
    <ReimbursementsTabs selectedOfferer={defaultGetOffererResponseModel} />,
    {
      features: isSettlementEnable ? ['WIP_ENABLE_FINANCE_SETTLEMENTS'] : [],
    }
  )

describe('ReimbursementsTabs', () => {
  it('should render ReimbursementsTabs with FF WIP_ENABLE_FINANCE_SETTLEMENTS ON', () => {
    renderReimbursementsTabs(true)

    expect(screen.getByRole('link', { name: /Virements/ })).toBeVisible()
    expect(screen.getByRole('link', { name: /Justificatifs/ })).toBeVisible()
    expect(
      screen.getByRole('link', { name: /Informations bancaires/ })
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: /Chiffre d’affaires/ })
    ).toBeVisible()
  })

  it('should render ReimbursementsTabs with FF WIP_ENABLE_FINANCE_SETTLEMENTS OFF', () => {
    renderReimbursementsTabs(false)

    expect(
      screen.queryByRole('link', { name: /Virements/ })
    ).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Justificatifs/ })).toBeVisible()
    expect(
      screen.getByRole('link', { name: /Informations bancaires/ })
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: /Chiffre d’affaires/ })
    ).toBeVisible()
  })

  it.each([
    { tabName: /Virements/, event: FinanceEvents.CLICKED_SETTLEMENTS_TAB },
    { tabName: /Justificatifs/, event: FinanceEvents.CLICKED_INVOICES_TAB },
    {
      tabName: /Informations bancaires/,
      event: FinanceEvents.CLICKED_BANK_INFO_TAB,
    },
    { tabName: /Chiffre d’affaires/, event: FinanceEvents.CLICKED_REVENUE_TAB },
  ])(
    'should log an event on tab $tabName click',
    async ({ tabName, event }) => {
      const user = userEvent.setup()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      renderReimbursementsTabs(true)

      await user.click(screen.getByRole('link', { name: tabName }))
      expect(mockLogEvent).toHaveBeenCalledExactlyOnceWith(event)
    }
  )
})
