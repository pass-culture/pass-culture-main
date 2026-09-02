import { screen } from '@testing-library/react'

import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { SettingsTabs } from './SettingsTabs'

const renderSettingsTabs = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<SettingsTabs />, {
    ...options,
  })
}

describe('SettingsTabs', () => {
  it('should display the fourth tab when the close venue feature flag is activated', () => {
    renderSettingsTabs({ features: ['WIP_CLOSE_VENUE'] })

    expect(
      screen.getByRole('link', { name: /Informations générales/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Notifications/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Synchronisations/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Gestion de la structure/ })
    ).toBeInTheDocument()
  })

  it('should hide the fourth tab when the close venue feature flag is deactivated', () => {
    renderSettingsTabs({ features: [] })

    expect(
      screen.getByRole('link', { name: /Informations générales/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Notifications/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Synchronisations/ })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('link', { name: /Gestion de la structure/ })
    ).not.toBeInTheDocument()
  })
})
