import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import OfferBreadcrumb, {
  OfferBreadcrumbStep,
  IOfferBreadcrumb,
} from '../OfferBreadcrumb'

const renderOfferBreadcrumb = (props: IOfferBreadcrumb) => {
  return render(
    <MemoryRouter>
      <OfferBreadcrumb {...props} />
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

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Stocks et prix')
      expect(listItems[2]).toHaveTextContent('Récapitulatif')
      expect(listItems[3]).toHaveTextContent('Confirmation')
    })

    it('should display breadcrumb for individual offer in edition', async () => {
      props.isCreatingOffer = false
      renderOfferBreadcrumb(props)

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
        '/offre/A1/individuel/recapitulatif'
      )
      expect(linkItems[1].getAttribute('href')).toBe(
        '/offre/A1/individuel/stocks'
      )
    })
  })

  describe('Collective offer - with domain association', () => {
    beforeEach(() => {
      props.isOfferEducational = true
    })

    it('should display breadcrumb for collective offer - with visibility step', async () => {
      props.isCreatingOffer = true
      renderOfferBreadcrumb(props)

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Date et prix')
      expect(listItems[2]).toHaveTextContent('Visibilité')
      expect(listItems[3]).toHaveTextContent('Confirmation')
    })

    it('should generate link with offerId when user is editing an offer', async () => {
      props.isCreatingOffer = false
      renderOfferBreadcrumb(props)

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
