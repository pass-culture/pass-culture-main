import { axe } from 'vitest-axe'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInformationsForm } from './CollectiveOfferInformationsForm'

describe('<CollectiveOfferInformationsForm />', () => {
  it('should render without accessibility violations', async () => {
    const offer = getCollectiveOfferFactory()
    const { container } = renderWithProviders(
      <CollectiveOfferInformationsForm offer={offer} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
