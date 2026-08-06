import { screen } from '@testing-library/dom'
import { axe } from 'vitest-axe'

import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferTemplateCreationNavigation,
  type CollectiveOfferTemplateCreationNavigationProps,
} from './CollectiveOfferTemplateCreationNavigation'
import { CollectiveOfferTemplateStep } from './constants'

const renderCollectiveOfferNavigation = (
  props: CollectiveOfferTemplateCreationNavigationProps
) =>
  renderWithProviders(<CollectiveOfferTemplateCreationNavigation {...props} />)

describe('<CollectiveOfferTemplateCreationNavigation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferTemplateStep.DETAILS,
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should show template offer steps', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferTemplateStep.SUMMARY,
      offer,
    })

    const listItems = await screen.findAllByRole('listitem')
    expect(listItems).toHaveLength(3)

    // Only the step preceding the active one is navigable.
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(1)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/vitrine/${offer.id}/creation`
    )
  })

  it('should link every step preceding the active one', () => {
    const offer = getCollectiveOfferTemplateFactory()
    renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferTemplateStep.PREVIEW,
      offer,
    })

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/vitrine/${offer.id}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/vitrine/creation/recapitulatif`
    )
  })
})
