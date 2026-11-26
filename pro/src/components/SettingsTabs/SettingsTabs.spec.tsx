import { screen } from '@testing-library/react'

import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { SettingsTabs } from './SettingsTabs'

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

const renderSettingsTabs = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<SettingsTabs />, {
    ...options,
  })
}

describe('SettingsTabs', () => {
  it('should display the fourth tab when the close venue feature flag is activated', () => {
    renderSettingsTabs({ features: ['WIP_CLOSE_VENUE'] })

    expect(
      screen.getByRole('tab', { name: /Informations générales/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('tab', { name: /Notifications/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('tab', { name: /Synchronisations/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('tab', { name: /Gestion de la structure/ })
    ).toBeInTheDocument()
  })

  it('should hide the fourth tab when the close venue feature flag is deactivated', () => {
    renderSettingsTabs({ features: [] })

    expect(
      screen.getByRole('tab', { name: /Informations générales/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('tab', { name: /Notifications/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('tab', { name: /Synchronisations/ })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('tab', { name: /Gestion de la structure/ })
    ).not.toBeInTheDocument()
  })
})
