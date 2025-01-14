import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { CardLink } from './CardLink'

const renderCardLink = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<CardLink />, { ...options })
}

describe('<CardLink />', () => {
  it('should render correctly', async () => {
    renderCardLink()

    expect(
      await screen.findByRole('heading', { name: /CardLink/ })
    ).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderCardLink()

    expect(await axe(container)).toHaveNoViolations()
  })
})
