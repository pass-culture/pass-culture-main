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

describe('src | components | OfferBreadcrumb', () => {
  let props: IOfferBreadcrumb

  beforeEach(() => {
    props = {
      activeStep: OfferBreadcrumbStep.DETAILS,
      isCreatingOffer: true,
      offerId: 'A1',
    }
  })

  describe('Collective offer - with domain association', () => {
    it('should display breadcrumb for collective offer - with visibility step in creation', async () => {
      props.isCreatingOffer = true
      renderOfferBreadcrumb(props)

      expect(screen.getByTestId('bc-default')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(5)
      expect(listItems[0]).toHaveTextContent('Détails de l’offre')
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
