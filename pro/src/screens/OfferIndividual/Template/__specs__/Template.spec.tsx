import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual } from 'core/Offers/types'

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
    reloadOffer: () => {},
    ...contextOverride,
  }
  return render(
    <OfferIndividualContext.Provider value={contextValues}>
      <MemoryRouter initialEntries={[url]}>
        <Template {...props}>
          <div>Template child</div>
        </Template>
      </MemoryRouter>
    </OfferIndividualContext.Provider>
  )
}

describe('test OfferIndividualStepper', () => {
  it('should render when no offer is given', async () => {
    await renderTemplate({})

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Informations')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
    expect(screen.getByText('Confirmation')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })
  it('should render when offer is given', async () => {
    const offer: Partial<IOfferIndividual> = {
      id: 'AA',
      name: "Titre de l'offre",
      stocks: [],
    }
    const contextOverride = {
      offer: offer as IOfferIndividual,
    }
    await renderTemplate({ contextOverride })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Informations')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.getByText('Récapitulatif')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: "Titre de l'offre" })
    ).toBeInTheDocument()
  })
  it('should render when no offer is given on edition mode', async () => {
    const offer: Partial<IOfferIndividual> = {
      id: 'AA',
      name: "Titre de l'offre",
      stocks: [],
    }
    const contextOverride = {
      offer: offer as IOfferIndividual,
    }
    await renderTemplate({
      contextOverride,
      url: '/offre/AA/v3/individuelle/informations',
    })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Informations')).toBeInTheDocument()
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

  it('should display custom title', async () => {
    await renderTemplate({ props: { title: 'Custom title' } })

    expect(
      screen.getByRole('heading', { name: 'Custom title' })
    ).toBeInTheDocument()
  })
})
