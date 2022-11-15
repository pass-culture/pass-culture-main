import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import CollectiveOfferBreadcrumb, {
  CollectiveOfferBreadcrumbStep,
  IOfferBreadcrumb,
} from '../CollectiveOfferBreadcrumb'

const renderCollectiveOfferBreadcrumb = (props: IOfferBreadcrumb) => {
  const store = configureTestStore()
  return render(
    <MemoryRouter>
      <Provider store={store}>
        <CollectiveOfferBreadcrumb {...props} />
      </Provider>
    </MemoryRouter>
  )
}

describe('src | components | CollectiveOfferBreadcrumb', () => {
  let props: IOfferBreadcrumb

  beforeEach(() => {
    props = {
      activeStep: CollectiveOfferBreadcrumbStep.DETAILS,
      isCreatingOffer: true,
      offerId: 'A1',
      isOfferEducational: true,
      isTemplate: false,
    }
  })

  it('should display breadcrumb for collective offer in creation', async () => {
    renderCollectiveOfferBreadcrumb(props)

    expect(screen.getByTestId('stepper')).toBeInTheDocument()

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(5)
    expect(listItems[0]).toHaveTextContent("Détails de l'offre")
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
      '/offre/collectif/vitrine/A1/creation'
    )
  })

  it('should show links if stocks is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.STOCKS
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(1)
    expect(links[0].getAttribute('href')).toBe('/offre/collectif/A1/creation')
  })

  it('should show links if visibility is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.VISIBILITY
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0].getAttribute('href')).toBe('/offre/collectif/A1/creation')
    expect(links[1].getAttribute('href')).toBe('/offre/A1/collectif/stocks')
  })

  it('should show links if summary is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.SUMMARY
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe('/offre/collectif/A1/creation')
    expect(links[1].getAttribute('href')).toBe('/offre/A1/collectif/stocks')
    expect(links[2].getAttribute('href')).toBe('/offre/A1/collectif/visibilite')
  })

  it('should show links if summary is the active step', async () => {
    props.activeStep = CollectiveOfferBreadcrumbStep.CONFIRMATION
    renderCollectiveOfferBreadcrumb(props)
    const links = await screen.queryAllByRole('link')
    expect(links).toHaveLength(4)
    expect(links[0].getAttribute('href')).toBe('/offre/collectif/A1/creation')
    expect(links[1].getAttribute('href')).toBe('/offre/A1/collectif/stocks')
    expect(links[2].getAttribute('href')).toBe('/offre/A1/collectif/visibilite')
    expect(links[3].getAttribute('href')).toBe(
      '/offre/A1/collectif/creation/recapitulatif'
    )
  })

  it('should generate link with offerId when user is editing an offer', async () => {
    props.isCreatingOffer = false
    renderCollectiveOfferBreadcrumb(props)

    expect(screen.getByTestId('bc-tab')).toBeInTheDocument()

    const linkItems = await screen.findAllByRole('link')

    expect(linkItems).toHaveLength(3)
    expect(linkItems[0].getAttribute('href')).toBe(
      '/offre/A1/collectif/edition'
    )
    expect(linkItems[1].getAttribute('href')).toBe(
      '/offre/A1/collectif/stocks/edition'
    )
    expect(linkItems[2].getAttribute('href')).toBe(
      '/offre/A1/collectif/visibilite/edition'
    )
  })
})
