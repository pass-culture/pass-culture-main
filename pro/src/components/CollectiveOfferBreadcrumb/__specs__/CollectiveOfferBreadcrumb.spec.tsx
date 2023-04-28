import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferBreadcrumb, {
  CollectiveOfferBreadcrumbStep,
  IOfferBreadcrumb,
} from '../CollectiveOfferBreadcrumb'

const renderCollectiveOfferBreadcrumb = (props: IOfferBreadcrumb) =>
  renderWithProviders(<CollectiveOfferBreadcrumb {...props} />)

describe('src | components | CollectiveOfferBreadcrumb', () => {
  let props: IOfferBreadcrumb
  const offerId = 1

  beforeEach(() => {
    props = {
      activeStep: CollectiveOfferBreadcrumbStep.DETAILS,
      isCreatingOffer: true,
      offerId: offerId,
      isOfferEducational: true,
      isTemplate: false,
    }
  })

  it('should display breadcrumb for collective offer in creation', async () => {
    props.offerId = 0
    renderCollectiveOfferBreadcrumb(props)

    expect(screen.getByTestId('stepper')).toBeInTheDocument()

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(5)
    expect(listItems[0]).toHaveTextContent('Détails de l’offre')
    expect(listItems[1]).toHaveTextContent('Date et prix')
    expect(listItems[2]).toHaveTextContent('Visibilité')
    expect(listItems[3]).toHaveTextContent('Récapitulatif')
    expect(listItems[4]).toHaveTextContent('Confirmation')

    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(0)
  })

  it('should show different links if offer is template', async () => {
    props.isTemplate = true
    props.activeStep = CollectiveOfferBreadcrumbStep.SUMMARY
    renderCollectiveOfferBreadcrumb(props)

    const listItems = await screen.findAllByRole('listitem')
    expect(listItems).toHaveLength(3)
    expect(screen.queryByText('Date et prix')).not.toBeInTheDocument()
    expect(screen.queryByText('Visibilité')).not.toBeInTheDocument()

    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(1)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/vitrine/${offerId}/creation`
    )
  })

  it('should show links if stocks is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.STOCKS
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
  })

  it('should show links if visibility is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.VISIBILITY
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
  })

  it('should show links if summary is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.SUMMARY
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite`
    )
  })

  it('should show links if summary is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.CONFIRMATION
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(4)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite`
    )
    expect(links[3].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/creation/recapitulatif`
    )
  })

  it('should generate link with offerId when user is editing an offer', async () => {
    props.isCreatingOffer = false
    renderCollectiveOfferBreadcrumb(props)

    expect(screen.getByTestId('bc-tab')).toBeInTheDocument()

    const linkItems = await screen.findAllByRole('link')

    expect(linkItems).toHaveLength(3)
    expect(linkItems[0].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/edition`
    )
    expect(linkItems[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks/edition`
    )
    expect(linkItems[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite/edition`
    )
  })

  it('should generate link for visibility and summary if offer has a stock', async () => {
    props.haveStock = true
    renderCollectiveOfferBreadcrumb(props)

    const links = await screen.findAllByRole('link')

    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/creation/recapitulatif`
    )
  })
})
