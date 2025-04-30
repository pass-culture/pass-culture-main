import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { AddressSelect } from './AddressSelect'

const renderAddressSelect = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<AddressSelect />, { ...options })
}

describe('<AddressSelect />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderAddressSelect()

    expect(await axe(container)).toHaveNoViolations()
  })
})
