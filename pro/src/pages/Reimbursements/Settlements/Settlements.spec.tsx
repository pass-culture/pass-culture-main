import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { vi } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { SettlementStatus } from '@/apiClient/v1'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Settlements } from './Settlements'

const BASE_SETTLEMENTS = [
  {
    id: 1,
    label: 'VIR-2024-001',
    date: '2024-06-01',
    bankAccount: 'Compte principal',
    status: SettlementStatus.EXECUTED,
    amount: 150,
    invoicesCount: 3,
  },
] as never

const renderSettlements = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()

  return renderWithProviders(<Settlements />, {
    user,
    ...options,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedAdminOfferer: defaultGetOffererResponseModel,
      },
    },
  })
}

describe('<Settlements />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'hasSettlement').mockResolvedValue({ hasSettlement: true })
    vi.spyOn(api, 'getSettlements').mockResolvedValue(BASE_SETTLEMENTS)
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await axe(container)).toHaveNoViolations()
  })

  it('fetches and renders the settlements for the selected offerer', async () => {
    renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.hasSettlement).toHaveBeenCalledWith({
      query: { offererId: defaultGetOffererResponseModel.id },
    })
    expect(api.getSettlements).toHaveBeenCalledWith({
      query: { offererId: defaultGetOffererResponseModel.id },
    })
    expect(screen.getByText('VIR-2024-001')).toBeInTheDocument()
  })

  it('does not fetch the settlements list and shows the empty state when hasSettlement is false', async () => {
    vi.spyOn(api, 'hasSettlement').mockResolvedValue({ hasSettlement: false })

    renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getSettlements).not.toHaveBeenCalled()
    // hasBankAccount is currently hardcoded to true in Settlements.tsx (see
    // the TODO comment in the source), so the "no bank account" empty state
    // is unreachable through this component for now.
    expect(
      screen.getByText('Aucun virement pour le moment')
    ).toBeInTheDocument()
  })
})
