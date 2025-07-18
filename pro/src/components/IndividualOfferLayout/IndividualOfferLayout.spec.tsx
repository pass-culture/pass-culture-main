import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { Route, Routes } from 'react-router'

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
  IndividualOfferLayout,
  IndividualOfferLayoutProps,
} from './IndividualOfferLayout'

const renderIndividualOfferLayout = (
  props: Partial<IndividualOfferLayoutProps>,
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
            <IndividualOfferLayout
              title="layout title"
              withStepper
              offer={getIndividualOfferFactory()}
              mode={OFFER_WIZARD_MODE.EDITION}
              {...props}
            >
              <div>Template child</div>
            </IndividualOfferLayout>
          }
        />
        <Route
          path="/onboarding/offre/creation"
          element={
            <IndividualOfferLayout
              title="layout title"
              withStepper
              offer={getIndividualOfferFactory()}
              mode={OFFER_WIZARD_MODE.EDITION}
              {...props}
            >
              <div>Template child</div>
            </IndividualOfferLayout>
          }
        />
        <Route path="/accueil" element={<div>Accueil</div>} />
      </Routes>
    </>,
    options
  )
}

describe('IndividualOfferLayout', () => {
  it('should render when no offer is given', () => {
    renderIndividualOfferLayout({ offer: null })

    expect(screen.getByText('Template child')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Stock & Prix')).toBeInTheDocument()
  })

  it('should render when offer is given', () => {
    const offer = getIndividualOfferFactory({
      name: 'offer name',
    })

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(screen.getByText('Mettre en pause')).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should not allow access to publication dates edition when offer is synchronized with a provider', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Boost' },
    })

    renderIndividualOfferLayout(
      {
        offer,
      },
      {
        features: ['WIP_REFACTO_FUTURE_OFFER'],
        initialRouterEntries: ['/offre/creation'],
      }
    )

    expect(screen.getByText('publiée')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should display status but not let activate offer when offer is synchronized with a provider', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Boost' },
    })

    renderIndividualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Mettre en pause' })
    ).not.toBeInTheDocument()
  })
  it('should display status but not let activate offer when offer is rejected', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.REJECTED,
    })

    renderIndividualOfferLayout({
      offer,
    })

    expect(screen.getByTestId('status')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Mettre en pause' })
    ).not.toBeInTheDocument()
  })

  it('should not display status in creation', () => {
    const offer = getIndividualOfferFactory({
      isActive: false,
      status: OfferStatus.DRAFT,
    })

    renderIndividualOfferLayout({
      offer,
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    expect(screen.queryByTestId('status')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Mettre en pause' })
    ).not.toBeInTheDocument()
  })

  it('should display provider banner', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Boost' },
    })

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
      offer,
    })

    expect(screen.queryByText('Offre synchronisée')).not.toBeInTheDocument()
  })

  it('should display publication date when it is in the future', () => {
    const future = addDays(new Date(), 3)

    renderIndividualOfferLayout({
      offer: getIndividualOfferFactory({
        publicationDate: future.toISOString(),
        status: OfferStatus.INACTIVE,
      }),
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    expect(screen.getByText(/Publication prévue le/)).toBeInTheDocument()
  })

  it('should not display publication date when it is passed', () => {
    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout(
      {
        offer,
      },
      {
        initialRouterEntries: ['/offre/creation'],
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

      renderIndividualOfferLayout(
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

      renderIndividualOfferLayout(
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
    renderIndividualOfferLayout({
      venueHasPublishedOfferWithSameEan: true,
    })

    expect(
      screen.getByRole('button', { name: 'Supprimer ce brouillon' })
    ).toBeInTheDocument()
  })

  it('should remove the draft offer if the user clicks on "Supprimer ce brouillon"', async () => {
    const offer = getIndividualOfferFactory({ status: OfferStatus.DRAFT })

    const spy = vi.spyOn(api, 'deleteDraftOffers').mockResolvedValueOnce()

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
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

    renderIndividualOfferLayout({
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

  it('should show the update publication button when the FF WIP_REFACTO_FUTURE_OFFER is enabled', () => {
    renderIndividualOfferLayout(
      {
        offer: getIndividualOfferFactory({
          status: OfferStatus.PUBLISHED,
          isEvent: true,
        }),
        children: <></>,
      },
      {
        features: ['WIP_REFACTO_FUTURE_OFFER'],
        initialRouterEntries: ['/offre/creation'],
      }
    )

    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should not show the update publication button when the FF WIP_REFACTO_FUTURE_OFFER is disabled', () => {
    renderIndividualOfferLayout({
      offer: getIndividualOfferFactory({
        status: OfferStatus.PUBLISHED,
        isEvent: true,
      }),
      children: <></>,
    })

    expect(
      screen.queryByRole('button', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should not show the update publication button when the offer is not published, inactive or scheduled', () => {
    renderIndividualOfferLayout(
      {
        offer: getIndividualOfferFactory({
          status: OfferStatus.EXPIRED,
          isEvent: true,
        }),
        children: <></>,
      },
      {
        features: ['WIP_REFACTO_FUTURE_OFFER'],
        initialRouterEntries: ['/offre/creation'],
      }
    )

    expect(
      screen.queryByRole('button', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })
})
