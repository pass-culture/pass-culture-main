import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOffersCTA } from './IndividualOffersCTA'

describe('<IndividualOffersCTA />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <IndividualOffersCTA offerLink="" />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
