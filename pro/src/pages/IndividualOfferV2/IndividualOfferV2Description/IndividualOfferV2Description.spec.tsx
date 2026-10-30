import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferV2Description } from './IndividualOfferV2Description'

describe('<IndividualOfferV2Description />', () => {
  it('should have no accessibility violations', async () => {
    const { container } = renderWithProviders(<IndividualOfferV2Description />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
