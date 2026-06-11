import { axe } from 'vitest-axe'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferInformationsForm,
  type CollectiveOfferInformationsFormProps,
} from './CollectiveOfferInformationsForm'

function renderCollectiveOfferInformationForm(
  props: Partial<CollectiveOfferInformationsFormProps>
) {
  const allProps = {
    offer: getCollectiveOfferFactory(),
    isCreation: true,
    saveAndContinue: vi.fn(),
    goBackLink: '/test/go/back/link',
    ...props,
  }
  return renderWithProviders(<CollectiveOfferInformationsForm {...allProps} />)
}

describe('<CollectiveOfferInformationsForm />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferInformationForm({})

    expect(await axe(container)).toHaveNoViolations()
  })
})
