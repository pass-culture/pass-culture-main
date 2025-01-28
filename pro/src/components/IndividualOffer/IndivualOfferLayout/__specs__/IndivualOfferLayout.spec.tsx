import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { Route } from 'react-router'
import { Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import * as useHasAccessToDidacticOnboarding from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

import {
  IndivualOfferLayout,
  IndivualOfferLayoutProps,
} from '../IndivualOfferLayout'

const renderIndivualOfferLayout = (
  props: Partial<IndivualOfferLayoutProps>,
  options: RenderWithProvidersOptions = {
    initialRouterEntries: ['/offre/creation'],
  }
) => {
  renderWithProviders(
    <>
      <Notification />
      <Routes>
        <Route
          path="/offre/creation"
          element={
            <IndivualOfferLayout
              title="layout title"
              withStepper
              offer={getIndividualOfferFactory()}
              mode={OFFER_WIZARD_MODE.EDITION}
              {...props}
            >
              <div>Template child</div>
            </IndivualOfferLayout>
          }
        />
        <Route
          path="/onboarding/offre/creation"
          element={
            <IndivualOfferLayout
              title="layout title"
              withStepper
              offer={getIndividualOfferFactory()}
              mode={OFFER_WIZARD_MODE.EDITION}
              {...props}
            >
              <div>Template child</div>
            </IndivualOfferLayout>
          }
        />
        <Route path="/accueil" element={<div>Accueil</div>} />
      </Routes>
    </>,
    options
  )
}

describe('IndivualOfferLayout', () => {
  it('should render when no offer is given', () => {
    renderIndivualOfferLayout({ offer: null })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
  })

  it('should render when offer is given', () => {
    const offer = getIndividualOfferFactory({
      name: 'offer name',
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()

    expect(screen.getByText(/offer name/)).toBeInTheDocument()
    expect(screen.getByText(/layout title/)).toBeInTheDocument()
  })

  it('should not display stepper nor status when no stepper', () => {
    const offer = getIndividualOfferFactory({
      isActive: true,
      status: OfferStatus.ACTIVE,
    })

    renderIndivualOfferLayout({
      offer,
      withStepper: false,
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
    expect(screen.queryByText('Détails de l’offre')).not.toBeInTheDocument()
    expect(screen.queryByText('Stock & Prix')).not.toBeInTheDocument()
  })

  it('should display status and button in edition', () => {
    const offer = getIndividualOfferFactory({
      isActive: true,
      status: OfferStatus.ACTIVE,
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(screen.getByText('Désactiver')).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display status but not let activate offer when offer is not activable', () => {
    const offer = getIndividualOfferFactory({
      isActivable: false,
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Désactiver' })
    ).not.toBeInTheDocument()
  })

  it('should not display status in creation', () => {
    const offer = getIndividualOfferFactory({
      isActive: false,
      status: OfferStatus.DRAFT,
    })

    renderIndivualOfferLayout({
      offer,
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Désactiver' })
    ).not.toBeInTheDocument()
  })

  it('should display provider banner', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Boost' },
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(
      screen.getByText('Offre synchronisée avec Boost')
    ).toBeInTheDocument()
  })

  it('should not display provider banner when no provider is provided', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: '' },
    })

    renderIndivualOfferLayout({
      offer,
    })

    expect(screen.queryByText('Offre synchronisée')).not.toBeInTheDocument()
  })

  it('should display publication date when it is in the future', () => {
    const future = addDays(new Date(), 3)

    renderIndivualOfferLayout({
      offer: getIndividualOfferFactory({
        publicationDate: future.toISOString(),
        status: OfferStatus.INACTIVE,
      }),
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    expect(screen.getByText(/Publication prévue le/)).toBeInTheDocument()
  })

  it('should not display publication date when it is passed', () => {
    renderIndivualOfferLayout({
      offer: getIndividualOfferFactory({
        publicationDate: '2021-01-01T00:00:00.000Z',
        status: OfferStatus.INACTIVE,
      }),
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    expect(screen.queryByText(/Publication prévue le/)).not.toBeInTheDocument()
  })

  it('should not display publication date in creation', () => {
    const future = addDays(new Date(), 3)

    renderIndivualOfferLayout({
      offer: getIndividualOfferFactory({
        publicationDate: future.toISOString(),
        status: OfferStatus.INACTIVE,
      }),
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    expect(screen.queryByText(/Publication prévue le/)).not.toBeInTheDocument()
  })

  it('should not display publication date if offer is published', () => {
    const future = addDays(new Date(), 3)

    renderIndivualOfferLayout({
      offer: getIndividualOfferFactory({
        publicationDate: future.toISOString(),
        status: OfferStatus.ACTIVE,
      }),
    })

    expect(screen.queryByText(/Publication prévue le/)).not.toBeInTheDocument()
  })

  it('should display a proper tag when offer is an headline offer and feature is active', () => {
    const offer = getIndividualOfferFactory({
      isHeadlineOffer: true,
    })

    renderIndivualOfferLayout(
      {
        offer,
      },
      {
        initialRouterEntries: ['/offre/creation'],
        features: ['WIP_HEADLINE_OFFER'],
      }
    )

    expect(screen.getByText('Offre à la une')).toBeInTheDocument()
  })

  describe('onboarding', () => {
    const options = { initialRouterEntries: ['/onboarding/offre/creation'] }

    it("Should redirect to homepage if the user can't access it and is on onboarding url", async () => {
      vi.spyOn(
        useHasAccessToDidacticOnboarding,
        'useHasAccessToDidacticOnboarding'
      ).mockReturnValue(false)

      renderIndivualOfferLayout(
        {
          offer: getIndividualOfferFactory(),
        },
        options
      )
      await waitFor(() => {
        expect(screen.getByText('Accueil')).toBeInTheDocument()
      })
    })

    it('Should display the page if the user can access onboarding and is on onboarding url', async () => {
      vi.spyOn(
        useHasAccessToDidacticOnboarding,
        'useHasAccessToDidacticOnboarding'
      ).mockReturnValue(true)

      renderIndivualOfferLayout(
        {
          offer: getIndividualOfferFactory(),
        },
        options
      )
      await waitFor(() => {
        expect(screen.getByText('Template child')).toBeInTheDocument()
      })
    })
  })

  it('should display an error callout if another offer exists with the same EAN', () => {
    renderIndivualOfferLayout({
      venueHasPublishedOfferWithSameEan: true,
    })

    expect(
      screen.getByRole('button', { name: 'Supprimer ce brouillon' })
    ).toBeInTheDocument()
  })

  it('should remove the draft offer if the user clicks on "Supprimer ce brouillon"', async () => {
    const offer = getIndividualOfferFactory({ status: OfferStatus.DRAFT })

    const spy = vi.spyOn(api, 'deleteDraftOffers').mockResolvedValueOnce()

    renderIndivualOfferLayout({
      offer,
      venueHasPublishedOfferWithSameEan: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer ce brouillon' })
    )

    expect(spy).toHaveBeenCalledWith({ ids: [offer.id] })

    expect(
      await screen.findByText('Votre brouillon a bien été supprimé')
    ).toBeInTheDocument()
  })

  it('should not remove the draft offer if the offer does not exist', async () => {
    const spy = vi.spyOn(api, 'deleteDraftOffers').mockResolvedValueOnce()

    renderIndivualOfferLayout({
      offer: null,
      venueHasPublishedOfferWithSameEan: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer ce brouillon' })
    )
    expect(spy).not.toHaveBeenCalled()
  })

  it('should show an error message if the deletion failed', async () => {
    vi.spyOn(api, 'deleteDraftOffers').mockRejectedValueOnce(new Error('error'))

    renderIndivualOfferLayout({
      venueHasPublishedOfferWithSameEan: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer ce brouillon' })
    )
    expect(
      await screen.findByText(
        'Une erreur s’est produite lors de la suppression de l’offre'
      )
    ).toBeInTheDocument()
  })
})
