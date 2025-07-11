import { screen } from '@testing-library/react'

import { collectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OfferNameCell, OfferNameCellProps } from './OfferNameCell'

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
    })

    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
    expect(screen.getByText('Offre nom')).toBeInTheDocument()
  })

  it('should not display tag when offer is not a template', () => {
    const offer = collectiveOfferFactory({ isShowcase: false, name: 'Test' })

    renderOfferNameCell({ offer, offerLink: '#', rowId: 'rowId' })

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
    })

    expect(screen.queryByRole('presentation')).not.toBeInTheDocument()
  })

  it('should display the mobile label when displayLabel is true', () => {
    const offer = collectiveOfferFactory({ name: 'Test' })

    renderOfferNameCell({
      offer,
      offerLink: '#',
      rowId: 'rowId',
      displayLabel: true,
    })

    expect(screen.getByText(/Nom de l’offre|Nom/i)).toBeInTheDocument()
  })

  it('should use the correct link for the offer', () => {
    const offer = collectiveOfferFactory({ name: 'Link test' })

    renderOfferNameCell({
      offer,
      offerLink: '/offre/123',
      rowId: 'rowId',
    })

    expect(screen.getByRole('link')).toHaveAttribute('href', '/offre/123')
  })
})
