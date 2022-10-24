import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import OfferBreadcrumb, {
  OfferBreadcrumbStep,
  IOfferBreadcrumb,
} from '../OfferBreadcrumb'

const renderOfferBreadcrumb = (props: IOfferBreadcrumb) => {
  const store = configureTestStore()
  return render(
    <MemoryRouter>
      <Provider store={store}>
        <OfferBreadcrumb {...props} />
      </Provider>
    </MemoryRouter>
  )
}

describe('src | new_components | OfferBreadcrumb', () => {
  let props: IOfferBreadcrumb

  beforeEach(() => {
    props = {
      activeStep: OfferBreadcrumbStep.DETAILS,
      isCreatingOffer: true,
      offerId: 'A1',
      isOfferEducational: false,
    }
  })

  describe('Individual offer', () => {
    it('should display breadcrumb for individual offer in creation', async () => {
      renderOfferBreadcrumb(props)

      expect(screen.getByTestId('stepper')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Stocks et prix')
      expect(listItems[2]).toHaveTextContent('Récapitulatif')
      expect(listItems[3]).toHaveTextContent('Confirmation')
      const links = await screen.findAllByRole('link')

      expect(links).toHaveLength(2)
      expect(links[0]).toHaveAttribute(
        'href',
        expect.stringContaining('creation')
      )
      expect(links[1]).toHaveAttribute(
        'href',
        expect.stringContaining('creation')
      )
    })

    it('should display breadcrumb for individual offer in edition', async () => {
      props.isCreatingOffer = false
      renderOfferBreadcrumb(props)

      expect(screen.getByTestId('bc-tab')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(2)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Stocks et prix')
    })

    it('should generate link with offerId when user is editing an offer', async () => {
      props.isCreatingOffer = false
      renderOfferBreadcrumb(props)

      const linkItems = await screen.findAllByRole('link')

      expect(linkItems).toHaveLength(2)
      expect(linkItems[0].getAttribute('href')).toBe(
        '/offre/A1/individuel/edition'
      )
      expect(linkItems[1].getAttribute('href')).toBe(
        '/offre/A1/individuel/stocks'
      )
    })
    it('should display breadcrumb for individual offer in brouillon', async () => {
      props.isCreatingOffer = false
      props.isCompletingDraft = true
      renderOfferBreadcrumb(props)

      expect(await screen.getByTestId('stepper')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Stocks et prix')
      expect(listItems[2]).toHaveTextContent('Récapitulatif')
      expect(listItems[3]).toHaveTextContent('Confirmation')

      const links = await screen.findAllByRole('link')

      expect(links).toHaveLength(2)
      expect(links[0]).toHaveAttribute(
        'href',
        expect.stringContaining('brouillon')
      )
      expect(links[1]).toHaveAttribute(
        'href',
        expect.stringContaining('brouillon')
      )
    })
  })

  describe('Collective offer - with domain association', () => {
    beforeEach(() => {
      props.isOfferEducational = true
    })

    it('should display breadcrumb for collective offer - with visibility step in creation', async () => {
      props.isCreatingOffer = true
      renderOfferBreadcrumb(props)

      expect(screen.getByTestId('bc-default')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(5)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Date et prix')
      expect(listItems[2]).toHaveTextContent('Visibilité')
      expect(listItems[3]).toHaveTextContent('Récapitulatif')
      expect(listItems[4]).toHaveTextContent('Confirmation')
    })

    it('should generate link with offerId when user is editing an offer', async () => {
      props.isCreatingOffer = false
      renderOfferBreadcrumb(props)

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

    it('should not display visibility step if offer is showcase', async () => {
      props.isCreatingOffer = false
      props.offerId = 'T-A1'
      renderOfferBreadcrumb(props)

      const linkItems = await screen.findAllByRole('link')
      expect(linkItems).toHaveLength(2)
      expect(screen.queryByText('Visibilité')).not.toBeInTheDocument()
    })
  })
})
