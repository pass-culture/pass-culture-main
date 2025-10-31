import { screen } from '@testing-library/react'

import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { OfferNameCell, type OfferNameCellProps } from './OfferNameCell'

const renderOfferNameCell = (
  props: OfferNameCellProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(<OfferNameCell {...props} />, {
    initialRouterEntries: ['/offres'],
    ...options,
  })

describe('OfferNameCell', () => {
  it('should display a tag for offer template', () => {
    const eventOffer = collectiveOfferTemplateFactory({
      name: 'Offre nom',
    })

    renderOfferNameCell({
      offer: eventOffer,
    })

    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
    expect(screen.getByText('Offre nom')).toBeInTheDocument()
  })

  it('should not display tag when offer is not a template', () => {
    const offer = collectiveOfferFactory({
      name: 'Test',
    })

    renderOfferNameCell({
      offer,
    })

    expect(screen.queryByText('Offre vitrine')).not.toBeInTheDocument()
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('should render a thumbnail', () => {
    const offer = collectiveOfferFactory({ imageUrl: '/thumb.jpg' })

    renderOfferNameCell({
      offer,
    })

    expect(screen.getByRole('presentation')).toHaveAttribute(
      'src',
      '/thumb.jpg'
    )
  })

  it('should use the correct link for the offer', () => {
    const offer = collectiveOfferFactory({ name: 'Link test' })

    renderOfferNameCell({
      offer,
    })

    expect(screen.getByRole('link')).toHaveAttribute(
      'href',
      `/offre/${offer.id}/collectif/recapitulatif`
    )
  })

  it('should show offer id when offer is bookable', () => {
    const offer = collectiveOfferFactory({
      name: 'Link test',
    })

    renderOfferNameCell({
      offer,
    })
    const offerTitle = screen.getByRole('link', {
      name: `N°${offer.id} ${offer.name}`,
    })
    expect(offerTitle).toBeInTheDocument()
  })

  it('should not show offer id when offer is template', () => {
    const offer = collectiveOfferTemplateFactory({
      name: 'Link test',
    })

    renderOfferNameCell({
      offer,
    })
    const offerTitle = screen.getByRole('link', {
      name: `Offre vitrine ${offer.name}`,
    })
    expect(offerTitle).toBeInTheDocument()
  })
})
