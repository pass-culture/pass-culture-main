import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { SnackBarContainer } from '../SnackBarContainer/SnackBarContainer'
import {
  IndividualOfferLayout,
  type IndividualOfferLayoutProps,
} from './IndividualOfferLayout'

vi.mock('react-router', async () => ({
  ...(await vi.importActual<typeof import('react-router')>('react-router')),
  Navigate: vi.fn(),
}))
vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(),
}))

const renderIndividualOfferLayout: RenderComponentFunction<
  IndividualOfferLayoutProps,
  IndividualOfferContextValues
> = (params) => {
  const offer = params.props?.offer
  assertOrFrontendError(
    offer !== undefined,
    '`offer` must be defined in props.'
  )

  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: null,
    offerId: offer?.id ?? null,
    setIsEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    offer,
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }
  const props: IndividualOfferLayoutProps = {
    offer,
    children: <div>Template child</div>,
    ...params.props,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <SnackBarContainer />
      <IndividualOfferLayout {...props} />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('IndividualOfferLayout', () => {
  const eventOffer = getIndividualOfferFactory({
    id: 1,
    isEvent: true,
  })
  const nonEventOffer = getIndividualOfferFactory({
    id: 2,
    isEvent: false,
  })

  describe('when mode is CREATION', () => {
    beforeEach(() => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    })

    it('should render when no offer is given', () => {
      const props = { offer: null }

      renderIndividualOfferLayout({ props })

      expect(screen.getByText('Template child')).toBeInTheDocument()
      expect(screen.getByText('Description')).toBeInTheDocument()
      expect(screen.getByText('Tarifs')).toBeInTheDocument()
    })

    it('should render when offer is given', () => {
      const props = {
        offer: {
          ...nonEventOffer,
          name: 'offer name',
        },
      }

      renderIndividualOfferLayout({ props })

      expect(screen.getByText('Template child')).toBeInTheDocument()
      expect(screen.getByText('Description')).toBeInTheDocument()
      expect(screen.getByText('Tarifs')).toBeInTheDocument()
      expect(screen.getByText('Horaires')).toBeInTheDocument()

      expect(screen.getByText(/offer name/)).toBeInTheDocument()
    })

    it('should display status and button in edition', () => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)

      const props = {
        offer: {
          ...nonEventOffer,
          isActive: true,
          status: OfferStatus.ACTIVE,
        },
      }

      renderIndividualOfferLayout({ props })

      expect(
        screen.getByRole('button', { name: 'Modifier' })
      ).toBeInTheDocument()
      expect(screen.getByText('publiée')).toBeInTheDocument()
    })

    it('should not display status in creation', () => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)

      const offer = getIndividualOfferFactory({
        isActive: false,
        status: OfferStatus.DRAFT,
      })

      renderIndividualOfferLayout({ props: { offer } })

      expect(screen.queryByTestId('status')).not.toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Mettre en pause' })
      ).not.toBeInTheDocument()
    })

    it('should display provider banner', () => {
      const offer = getIndividualOfferFactory({
        lastProvider: { name: 'Boost' },
      })

      renderIndividualOfferLayout({ props: { offer } })

      expect(
        screen.getByText('Cette offre est synchronisée avec Boost')
      ).toBeInTheDocument()
    })

    it('should not display provider banner when no provider is provided', () => {
      const offer = getIndividualOfferFactory({
        lastProvider: { name: '' },
      })

      renderIndividualOfferLayout({ props: { offer } })

      expect(screen.queryByText('Offre synchronisée')).not.toBeInTheDocument()
    })

    it('should display highlight banner', () => {
      // Given
      const offer = getIndividualOfferFactory({
        status: OfferStatus.ACTIVE,
        isEvent: true,
      })

      // When
      renderIndividualOfferLayout({
        props: { offer },
      })

      // Then
      expect(
        screen.queryByRole('button', { name: 'Choisir un temps fort' })
      ).toBeInTheDocument()
    })

    it('should not display highlight banner if the offer is not an event', () => {
      // Given
      const offer = getIndividualOfferFactory({
        status: OfferStatus.ACTIVE,
        isEvent: false,
      })

      // When
      renderIndividualOfferLayout({
        props: { offer },
      })

      // Then
      expect(
        screen.queryByRole('button', { name: 'Choisir un temps fort' })
      ).not.toBeInTheDocument()
    })

    it('should not display highlight banner if the offer is rejected', () => {
      // Given
      const offer = getIndividualOfferFactory({
        status: OfferStatus.REJECTED,
        isEvent: true,
      })

      // When
      renderIndividualOfferLayout({
        props: { offer },
      })

      // Then
      expect(
        screen.queryByRole('button', { name: 'Choisir un temps fort' })
      ).not.toBeInTheDocument()
    })

    it('should not display highlight banner if the offer is pending', () => {
      // Given
      const offer = getIndividualOfferFactory({
        status: OfferStatus.PENDING,
        isEvent: true,
      })

      renderIndividualOfferLayout({
        props: { offer },
      })

      // Then
      expect(
        screen.queryByRole('button', { name: 'Choisir un temps fort' })
      ).not.toBeInTheDocument()
    })

    it('should not display highlight banner if the offer is pending', () => {
      // Given
      const offer = getIndividualOfferFactory({
        status: OfferStatus.DRAFT,
        isEvent: true,
      })

      renderIndividualOfferLayout({
        props: { offer },
      })

      // Then
      expect(
        screen.queryByRole('button', { name: 'Choisir un temps fort' })
      ).not.toBeInTheDocument()
    })

    it('should not display publication date in creation', () => {
      const future = addDays(new Date(), 3)
      const offer = getIndividualOfferFactory({
        publicationDate: future.toISOString(),
        status: OfferStatus.INACTIVE,
      })

      renderIndividualOfferLayout({ props: { offer } })

      expect(
        screen.queryByText(/Publication prévue le/)
      ).not.toBeInTheDocument()
    })

    it('should not display publication date if offer is published', () => {
      const props = {
        offer: {
          ...nonEventOffer,
          publicationDate: addDays(new Date(), 3).toISOString(),
          status: OfferStatus.ACTIVE,
        },
      }

      renderIndividualOfferLayout({ props })

      expect(
        screen.queryByText(/Publication prévue le/)
      ).not.toBeInTheDocument()
    })

    it('should display a proper tag when offer is an headline offer and feature is active', () => {
      const props = {
        offer: {
          ...nonEventOffer,
          isHeadlineOffer: true,
        },
      }

      renderIndividualOfferLayout({ props })

      expect(screen.getByText('Offre à la une')).toBeInTheDocument()
    })

    it('should display an error callout if another offer exists with the same EAN', () => {
      const contextValues = {
        hasPublishedOfferWithSameEan: true,
      }
      const props = { offer: nonEventOffer }

      renderIndividualOfferLayout({ contextValues, props })

      expect(
        screen.getByRole('button', { name: 'Supprimer ce brouillon' })
      ).toBeInTheDocument()
    })

    it('should remove the draft offer if the user clicks on "Supprimer ce brouillon"', async () => {
      const deleteDraftOffersSpy = vi
        .spyOn(api, 'deleteDraftOffers')
        .mockResolvedValueOnce()

      const offer = getIndividualOfferFactory({ status: OfferStatus.DRAFT })
      const contextValues = {
        hasPublishedOfferWithSameEan: true,
      }
      const props = { offer }

      renderIndividualOfferLayout({ props, contextValues })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer ce brouillon' })
      )

      expect(deleteDraftOffersSpy).toHaveBeenCalledWith({ ids: [offer.id] })

      expect(
        await screen.findByText('Votre brouillon a bien été supprimé')
      ).toBeInTheDocument()
    })

    it('should not remove the draft offer if the offer does not exist', async () => {
      const deleteDraftOffers = vi
        .spyOn(api, 'deleteDraftOffers')
        .mockResolvedValueOnce()

      const contextValues = {
        hasPublishedOfferWithSameEan: true,
      }
      const props = { offer: null }

      renderIndividualOfferLayout({ props, contextValues })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer ce brouillon' })
      )
      expect(deleteDraftOffers).not.toHaveBeenCalled()
    })

    it('should show an error message if the deletion failed', async () => {
      vi.spyOn(api, 'deleteDraftOffers').mockRejectedValueOnce(
        new Error('error')
      )

      const contextValues = {
        hasPublishedOfferWithSameEan: true,
      }
      const props = { offer: nonEventOffer }

      renderIndividualOfferLayout({ contextValues, props })

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer ce brouillon' })
      )
      expect(
        await screen.findByText(
          'Une erreur s’est produite lors de la suppression de l’offre'
        )
      ).toBeInTheDocument()
    })

    it('should not show the update publication button when the offer is not published, inactive or scheduled', () => {
      const options = {
        initialRouterEntries: ['/offre/creation'],
      }
      const props = {
        offer: {
          ...eventOffer,
          status: OfferStatus.EXPIRED,
        },
        children: <></>,
      }

      renderIndividualOfferLayout({ options, props })

      expect(
        screen.queryByRole('button', { name: 'Modifier' })
      ).not.toBeInTheDocument()
    })

    describe("when it's an onboarding path", () => {
      const options = {
        initialRouterEntries: [
          '/onboarding/offre/individuelle/creation/description',
        ],
      }

      it('Should display the page if the user can access onboarding and is on onboarding url', async () => {
        const props = { offer: nonEventOffer }

        renderIndividualOfferLayout({ options, props })

        await waitFor(() => {
          expect(screen.getByText('Template child')).toBeInTheDocument()
        })
      })
    })
  })

  describe('when mode is EDITION', () => {
    beforeEach(() => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    })

    it('should not allow access to publication dates edition when offer is synchronized with a provider', () => {
      const props = {
        offer: {
          ...nonEventOffer,
          lastProvider: { name: 'Boost' },
          status: OfferStatus.PUBLISHED,
        },
      }

      renderIndividualOfferLayout({ props })

      expect(screen.getByText('publiée')).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Modifier' })
      ).not.toBeInTheDocument()
    })

    it('should display status but not let activate offer when offer is synchronized with a provider', () => {
      const props = {
        offer: {
          ...nonEventOffer,
          lastProvider: { name: 'Boost' },
        },
      }

      renderIndividualOfferLayout({ props })

      expect(screen.getByTestId('status')).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Mettre en pause' })
      ).not.toBeInTheDocument()
    })

    it('should display status but not let activate offer when offer is rejected', () => {
      const offer = getIndividualOfferFactory({
        status: OfferStatus.REJECTED,
      })

      renderIndividualOfferLayout({ props: { offer } })

      expect(screen.getByTestId('status')).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Mettre en pause' })
      ).not.toBeInTheDocument()
    })
  })

  describe('when mode is READONLY', () => {
    beforeEach(() => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.READ_ONLY)
    })

    it('should not display publication date when it is passed', () => {
      const offer = getIndividualOfferFactory({
        publicationDate: '2021-01-01T00:00:00.000Z',
        status: OfferStatus.INACTIVE,
      })

      renderIndividualOfferLayout({ props: { offer } })

      expect(
        screen.queryByText(/Publication prévue le/)
      ).not.toBeInTheDocument()
    })

    it('should show the update publication button', () => {
      const options = {
        initialRouterEntries: ['/offre/creation'],
      }
      const props = {
        offer: {
          ...eventOffer,
          status: OfferStatus.PUBLISHED,
        },
      }

      renderIndividualOfferLayout({ options, props })

      expect(
        screen.getByRole('button', { name: 'Modifier' })
      ).toBeInTheDocument()
    })
  })
})
