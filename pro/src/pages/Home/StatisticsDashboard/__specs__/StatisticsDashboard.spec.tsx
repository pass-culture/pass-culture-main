import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { defautGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  StatisticsDashboard,
  StatisticsDashboardProps,
} from '../StatisticsDashboard'

vi.mock('apiClient/api', () => ({
  api: {
    getOffererStats: vi.fn(),
  },
}))

const renderStatisticsDashboard = (
  props: Partial<StatisticsDashboardProps> = {}
) =>
  renderWithProviders(
    <StatisticsDashboard
      offerer={{ ...defautGetOffererResponseModel, isValidated: true }}
      {...props}
    />
  )

describe('StatisticsDashboard', () => {
  it('should render empty state when no statistics', async () => {
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: null,
      syncDate: null,
      offererId: 1,
    })

    renderStatisticsDashboard()

    expect(screen.getByText('Présence sur le pass Culture')).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Créez vos premières offres grand public pour être visible par les bénéficiaires'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Dernière mise à jour : N/A')).toBeInTheDocument()
  })
})
