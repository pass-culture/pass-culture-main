import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { DMSModal } from './DMSModal'

const renderDMSModal = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<DMSModal />, { ...options })
}

describe('<DMSModal />', () => {
  it('should render correctly', async () => {
    renderDMSModal()

    expect(
      await screen.findByRole('heading', { name: /Quelles sont les étapes ?/ })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('link', { name: /Déposer un dossier/ })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
    ).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderDMSModal()

    expect(await axe(container)).toHaveNoViolations()
  })
})
