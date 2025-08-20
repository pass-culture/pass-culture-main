import { screen } from '@testing-library/react'

import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
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
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      name: 'Offre nom',
    })

    renderOfferNameCell({
      offer: eventOffer,
      offerLink: '#',
    })

    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
    expect(screen.getByText('Offre nom')).toBeInTheDocument()
  })

  it('should not display tag when offer is not a template', () => {
    const offer = collectiveOfferFactory({ isShowcase: false, name: 'Test' })

    renderOfferNameCell({ offer, offerLink: '#' })

    expect(screen.queryByText('Offre vitrine')).not.toBeInTheDocument()
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('should render a thumbnail', () => {
    const offer = collectiveOfferFactory({ imageUrl: '/thumb.jpg' })

    renderOfferNameCell({
      offer,
      offerLink: '#',
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
      offerLink: '/offre/123',
    })

    expect(screen.getByRole('link')).toHaveAttribute('href', '/offre/123')
  })
})
