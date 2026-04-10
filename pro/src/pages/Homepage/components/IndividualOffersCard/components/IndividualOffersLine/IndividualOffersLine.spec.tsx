import { axe } from 'vitest-axe'

import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOffersLine } from './IndividualOffersLine'

describe('<IndividualOffersLine />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <IndividualOffersLine offer={defaultOfferHomeResponseModel} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
