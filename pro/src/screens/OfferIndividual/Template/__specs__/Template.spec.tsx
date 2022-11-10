import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { OfferStatus } from 'apiClient/v1'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual } from 'core/Offers/types'
import { configureTestStore } from 'store/testUtils'

import Template, { ITemplateProps } from '../Template'

interface IRenderTemplateProps {
  contextOverride?: Partial<IOfferIndividualContext>
  url?: string
  props?: Partial<ITemplateProps>
}

const renderTemplate = ({
  contextOverride = {},
  url = '/offre/AA/v3/creation/individuelle/informations',
  props = {},
}: IRenderTemplateProps) => {
  const contextValues: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    ...contextOverride,
  }
  return render(
    <Provider store={configureTestStore({})}>
      <OfferIndividualContext.Provider value={contextValues}>
        <MemoryRouter initialEntries={[url]}>
          <Template {...props}>
            <div>Template child</div>
          </Template>
        </MemoryRouter>
      </OfferIndividualContext.Provider>
    </Provider>
  )
}

describe('test OfferIndividualTemplate', () => {
  it('should render when no offer is given', () => {
    renderTemplate({})

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText("Détails de l'offre")).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
    expect(screen.getByText('Confirmation')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })
  it('should render when offer is given', () => {
    const offer: Partial<IOfferIndividual> = {
      id: 'AA',
      name: "Titre de l'offre",
      stocks: [],
    }
    const contextOverride = {
      offer: offer as IOfferIndividual,
    }
    renderTemplate({ contextOverride })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText("Détails de l'offre")).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.getByText('Récapitulatif')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: "Titre de l'offre" })
    ).toBeInTheDocument()
  })
  it('should render when no offer is given on edition mode', () => {
    const offer: Partial<IOfferIndividual> = {
      id: 'AA',
      name: "Titre de l'offre",
      stocks: [],
    }
    const contextOverride = {
      offer: offer as IOfferIndividual,
    }
    renderTemplate({
      contextOverride,
      url: '/offre/AA/v3/individuelle/informations',
    })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText("Détails de l'offre")).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.queryByText('Récapitulatif')).not.toBeInTheDocument()
    expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: "Modifier l'offre" })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: "Titre de l'offre" })
    ).toBeInTheDocument()
  })

  it('should display custom title', () => {
    renderTemplate({ props: { title: 'Custom title' } })

    expect(
      screen.getByRole('heading', { name: 'Custom title' })
    ).toBeInTheDocument()
  })

  describe('Status', () => {
    it('should display status and button in edition', () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        name: "Titre de l'offre",
        isActive: true,
        status: OfferStatus.ACTIVE,
        stocks: [],
      }
      const contextOverride = {
        offer: offer as IOfferIndividual,
      }
      renderTemplate({
        contextOverride,
        url: '/offre/AA/v3/individuelle/informations',
      })

      expect(screen.getByTestId('status')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Désactiver' })
      ).toBeInTheDocument()
      expect(screen.getByText('publiée')).toBeInTheDocument()
    })

    it('should display draft status in draft', () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        name: "Titre de l'offre",
        isActive: false,
        status: OfferStatus.DRAFT,
        stocks: [],
      }
      const contextOverride = {
        offer: offer as IOfferIndividual,
      }
      renderTemplate({
        contextOverride,
        url: '/offre/AA/v3/brouillon/individuelle/informations',
      })

      expect(screen.getByTestId('status')).toBeInTheDocument()
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
      expect(screen.getByText('brouillon')).toBeInTheDocument()
    })

    it('should display nothing in creation', () => {
      const offer: Partial<IOfferIndividual> = {
        id: 'AA',
        name: "Titre de l'offre",
        isActive: false,
        status: OfferStatus.DRAFT,
        stocks: [],
      }
      const contextOverride = {
        offer: offer as IOfferIndividual,
      }
      renderTemplate({
        contextOverride,
      })

      expect(screen.queryByTestId('status')).not.toBeInTheDocument()
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })
  })
})
