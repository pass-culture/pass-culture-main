import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferNavigation, {
  CollectiveOfferStep,
  CollectiveOfferNavigationProps,
} from '../CollectiveOfferNavigation'

const renderCollectiveOfferNavigation = (
  props: CollectiveOfferNavigationProps
) => renderWithProviders(<CollectiveOfferNavigation {...props} />)

describe('CollectiveOfferNavigation', () => {
  let props: CollectiveOfferNavigationProps
  const offerId = 1

  beforeEach(() => {
    props = {
      activeStep: CollectiveOfferStep.DETAILS,
      isCreatingOffer: true,
      offerId: offerId,
      isOfferEducational: true,
      isTemplate: false,
    }
  })

  it('should display navigation for collective offer in creation', async () => {
    props.offerId = 0
    renderCollectiveOfferNavigation(props)

    expect(screen.getByTestId('stepper')).toBeInTheDocument()

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(5)
    expect(listItems[0]).toHaveTextContent('Détails de l’offre')
    expect(listItems[1]).toHaveTextContent('Date et prix')
    expect(listItems[2]).toHaveTextContent('Établissement et enseignant')
    expect(listItems[3]).toHaveTextContent('Récapitulatif')
    expect(listItems[4]).toHaveTextContent('Confirmation')

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(0)
  })

  it('should show different links if offer is template', async () => {
    props.isTemplate = true
    props.activeStep = CollectiveOfferStep.SUMMARY
    renderCollectiveOfferNavigation(props)

    const listItems = await screen.findAllByRole('listitem')
    expect(listItems).toHaveLength(4)
    expect(screen.queryByText('Date et prix')).not.toBeInTheDocument()
    expect(screen.queryByText('Visibilité')).not.toBeInTheDocument()

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/vitrine/${offerId}/creation`
    )
  })

  it('should show links if stocks is the active step', () => {
    props.activeStep = CollectiveOfferStep.STOCKS
    renderCollectiveOfferNavigation(props)
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
  })

  it('should show links if visibility is the active step', () => {
    props.activeStep = CollectiveOfferStep.VISIBILITY
    renderCollectiveOfferNavigation(props)
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
  })

  it('should show links if summary is the active step', () => {
    props.activeStep = CollectiveOfferStep.SUMMARY
    renderCollectiveOfferNavigation(props)
    const links = screen.queryAllByRole('link')
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
  })

  it('should show links if summary is the active step', () => {
    props.activeStep = CollectiveOfferStep.CONFIRMATION
    renderCollectiveOfferNavigation(props)
    const links = screen.queryAllByRole('link')
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
    renderCollectiveOfferNavigation(props)

    expect(
      screen.getByRole('link', { name: 'Date et prix' })
    ).toBeInTheDocument()

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
    renderCollectiveOfferNavigation(props)

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
