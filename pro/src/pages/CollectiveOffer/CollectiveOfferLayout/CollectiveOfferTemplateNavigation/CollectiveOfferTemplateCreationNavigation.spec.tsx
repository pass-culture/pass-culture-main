import { screen } from '@testing-library/dom'
import { axe } from 'vitest-axe'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferStep } from '../CollectiveOfferNavigation/CollectiveOfferCreationNavigation'
import {
  CollectiveOfferTemplateCreationNavigation,
  type CollectiveOfferTemplateCreationNavigationProps,
} from './CollectiveOfferTemplateCreationNavigation'

const renderCollectiveOfferNavigation = (
  props: CollectiveOfferTemplateCreationNavigationProps
) =>
  renderWithProviders(<CollectiveOfferTemplateCreationNavigation {...props} />)

describe('<CollectiveOfferTemplateCreationNavigation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should show different links if offer is template', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    renderCollectiveOfferNavigation({
      offerId: offer.id,
      activeStep: CollectiveOfferStep.SUMMARY,
      offer,
    })

    const listItems = await screen.findAllByRole('listitem')
    expect(listItems).toHaveLength(3)
    expect(screen.queryByText('Dates et prix')).not.toBeInTheDocument()
    expect(screen.queryByText('Visibilité')).not.toBeInTheDocument()

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/vitrine/${offer.id}/creation`
    )
  })

  it('should show links if confirmation is the active step and the offer is template', () => {
    const offer = getCollectiveOfferTemplateFactory()
    renderCollectiveOfferNavigation({
      offerId: offer.id,
      activeStep: CollectiveOfferStep.CONFIRMATION,
      offer,
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
  })

  it('should not show create bookable offer button if template offer has pending status', () => {
    const offer = getCollectiveOfferTemplateFactory({
      displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
    })
    renderCollectiveOfferNavigation({
      offerId: offer.id,
      offer,
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(
      screen.queryByRole('button', { name: 'Créer une offre réservable' })
    ).not.toBeInTheDocument()
  })
})
