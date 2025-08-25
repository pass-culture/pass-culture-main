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
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <OfferNameCell {...props} />
        </tr>
      </tbody>
    </table>,
    {
      initialRouterEntries: ['/offres'],
      ...options,
    }
  )

describe('OfferNameCell', () => {
  it('should display a tag for offer template', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      name: 'Offre nom',
    })

    renderOfferNameCell({
      offer: eventOffer,
      offerLink: '#',
      rowId: 'rowId',
      isNewCollectiveOffersStructureActive: false,
    })

    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
    expect(screen.getByText('Offre nom')).toBeInTheDocument()
  })

  it('should not display tag when offer is not a template', () => {
    const offer = collectiveOfferFactory({ isShowcase: false, name: 'Test' })

    renderOfferNameCell({
      offer,
      offerLink: '#',
      rowId: 'rowId',
      isNewCollectiveOffersStructureActive: false,
    })

    expect(screen.queryByText('Offre vitrine')).not.toBeInTheDocument()
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('should render a thumbnail when displayThumb is true', () => {
    const offer = collectiveOfferFactory({ imageUrl: '/thumb.jpg' })

    renderOfferNameCell({
      offer,
      offerLink: '#',
      rowId: 'rowId',
      displayThumb: true,
      isNewCollectiveOffersStructureActive: false,
    })

    expect(screen.getByRole('presentation')).toHaveAttribute(
      'src',
      '/thumb.jpg'
    )
  })

  it('should not render a thumbnail when displayThumb is false', () => {
    const offer = collectiveOfferFactory({ imageUrl: '/thumb.jpg' })

    renderOfferNameCell({
      offer,
      offerLink: '#',
      rowId: 'rowId',
      displayThumb: false,
      isNewCollectiveOffersStructureActive: false,
    })

    expect(screen.queryByRole('presentation')).not.toBeInTheDocument()
  })

  it('should use the correct link for the offer', () => {
    const offer = collectiveOfferFactory({ name: 'Link test' })

    renderOfferNameCell({
      offer,
      offerLink: '/offre/123',
      rowId: 'rowId',
      isNewCollectiveOffersStructureActive: false,
    })

    expect(screen.getByRole('link')).toHaveAttribute('href', '/offre/123')
  })

  it('should show offer id when WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE is active', () => {
    const offer = collectiveOfferFactory({
      name: 'Link test',
    })

    renderOfferNameCell(
      {
        offer,
        offerLink: '/offre/123',
        rowId: 'rowId',
        isNewCollectiveOffersStructureActive: true,
      },
      {
        features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'],
      }
    )
    const offerTitle = screen.getByRole('link', {
      name: `N°${offer.id} ${offer.name}`,
    })
    expect(offerTitle).toBeInTheDocument()
  })

  it('should not show offer id when WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE is active and offer is template', () => {
    const offer = collectiveOfferFactory({
      name: 'Link test',
      isShowcase: true,
    })

    renderOfferNameCell(
      {
        offer,
        offerLink: '/offre/123',
        rowId: 'rowId',
        isNewCollectiveOffersStructureActive: true,
      },
      {
        features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'],
      }
    )
    const offerTitle = screen.getByRole('link', {
      name: `Offre vitrine ${offer.name}`,
    })
    expect(offerTitle).toBeInTheDocument()
  })
})
