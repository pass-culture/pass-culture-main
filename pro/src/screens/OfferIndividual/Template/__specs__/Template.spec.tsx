import { screen } from '@testing-library/react'
import React from 'react'
import { generatePath } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  OfferIndividualContext,
  OfferIndividualContextValues,
} from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { OfferIndividual } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { renderWithProviders } from 'utils/renderWithProviders'

import Template, { TemplateProps } from '../Template'

interface RenderTemplateProps {
  contextOverride?: Partial<OfferIndividualContextValues>
  url?: string
  props?: Partial<TemplateProps>
}

const renderTemplate = ({
  contextOverride = {},
  url = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode: OFFER_WIZARD_MODE.CREATION,
  }),
  props = {},
}: RenderTemplateProps) => {
  const contextValues: OfferIndividualContextValues = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  return renderWithProviders(
    <OfferIndividualContext.Provider value={contextValues}>
      <Template {...props}>
        <div>Template child</div>
      </Template>
    </OfferIndividualContext.Provider>,
    { initialRouterEntries: [url] }
  )
}

describe('test OfferIndividualTemplate', () => {
  const offerId = 1
  it('should render when no offer is given', () => {
    renderTemplate({})

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.getByText('Récapitulatif')).toBeInTheDocument()
    expect(screen.getByText('Confirmation')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })
  it('should render when offer is given', () => {
    const offer: Partial<OfferIndividual> = {
      name: 'Titre de l’offre',
      id: offerId,
      stocks: [],
    }
    const contextOverride = {
      offer: offer as OfferIndividual,
    }
    renderTemplate({ contextOverride })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.getByText('Récapitulatif')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Titre de l’offre' })
    ).toBeInTheDocument()
  })
  it('should render when no offer is given on edition mode', () => {
    const offer: Partial<OfferIndividual> = {
      name: 'Titre de l’offre',
      id: offerId,
      stocks: [],
    }
    const contextOverride = {
      offer: offer as OfferIndividual,
    }
    renderTemplate({
      contextOverride,
      url: generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId: offerId }
      ),
    })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
    expect(screen.queryByText('Récapitulatif')).not.toBeInTheDocument()
    expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Modifier l’offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Titre de l’offre' })
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
      const offer: Partial<OfferIndividual> = {
        name: 'Titre de l’offre',
        id: offerId,
        isActive: true,
        status: OfferStatus.ACTIVE,
        stocks: [],
      }
      const contextOverride = {
        offer: offer as OfferIndividual,
      }
      renderTemplate({
        contextOverride,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: offerId }
        ),
      })

      expect(screen.getByTestId('status')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Désactiver' })
      ).toBeInTheDocument()
      expect(screen.getByText('publiée')).toBeInTheDocument()
    })

    it('should display draft status in draft', () => {
      const offer: Partial<OfferIndividual> = {
        name: 'Titre de l’offre',
        id: offerId,
        isActive: false,
        status: OfferStatus.DRAFT,
        stocks: [],
      }
      const contextOverride = {
        offer: offer as OfferIndividual,
      }
      renderTemplate({
        contextOverride,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: offerId }
        ),
      })

      expect(screen.getByTestId('status')).toBeInTheDocument()
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
      expect(screen.getByText('brouillon')).toBeInTheDocument()
    })

    it('should display nothing in creation', () => {
      const offer: Partial<OfferIndividual> = {
        name: 'Titre de l’offre',
        id: offerId,
        isActive: false,
        status: OfferStatus.DRAFT,
        stocks: [],
      }
      const contextOverride = {
        offer: offer as OfferIndividual,
      }
      renderTemplate({
        contextOverride,
      })

      expect(screen.queryByTestId('status')).not.toBeInTheDocument()
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })

    it('should display provider banner', () => {
      const offer: Partial<OfferIndividual> = {
        name: 'Titre de l’offre',
        id: offerId,
        isActive: false,
        status: OfferStatus.DRAFT,
        stocks: [],
        lastProviderName: 'boost',
      }
      const contextOverride = {
        offer: offer as OfferIndividual,
      }
      renderTemplate({
        contextOverride,
      })

      expect(
        screen.getByText('Offre synchronisée avec Boost')
      ).toBeInTheDocument()
    })

    it('should not display provider banner when no provider is provided', () => {
      const offer: Partial<OfferIndividual> = {
        name: 'Titre de l’offre',
        id: offerId,
        isActive: false,
        status: OfferStatus.DRAFT,
        stocks: [],
        lastProviderName: '',
      }
      const contextOverride = {
        offer: offer as OfferIndividual,
      }
      renderTemplate({
        contextOverride,
      })

      expect(screen.queryByText('Offre synchronisée')).not.toBeInTheDocument()
    })
  })
})
