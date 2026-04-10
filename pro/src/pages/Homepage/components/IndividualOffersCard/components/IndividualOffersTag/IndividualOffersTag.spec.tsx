import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'

import { IndividualOffersTag } from './IndividualOffersTag'

describe('<IndividualOffersTag />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <IndividualOffersTag offer={defaultOfferHomeResponseModel} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
