import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { MultiSelect } from './MultiSelect'

const renderMultiSelect = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<MultiSelect />, { ...options })
}

describe('<MultiSelect />', () => {
  it('should render correctly', async () => {
    renderMultiSelect()

    expect(
      await screen.findByRole('heading', { name: /MultiSelect/ })
    ).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderMultiSelect()

    expect(await axe(container)).toHaveNoViolations()
  })
})
