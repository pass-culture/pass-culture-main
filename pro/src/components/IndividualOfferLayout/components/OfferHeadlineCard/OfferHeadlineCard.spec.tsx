import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import * as HeadlineOfferContext from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferHeadlineCard } from './OfferHeadlineCard'

const MockHeadlineOfferImageDialogs = vi.fn(({ isFirstDialogOpen }) => (
  <div data-testid="HeadlineOfferImageDialogs">
    {isFirstDialogOpen ? 'Dialog Open' : 'Dialog Closed'}
  </div>
))

vi.mock(
  '@/pages/IndividualOffers/IndividualOffersContainer/components/IndividualOfferColumns/components/HeadlineOfferImageDialogs',
  () => ({
    HeadlineOfferImageDialogs: (props: any) =>
      MockHeadlineOfferImageDialogs(props),
  })
)

const mockUpsertHeadlineOffer = vi.fn()
const mockRemoveHeadlineOffer = vi.fn()

type RenderOptions = {
  offerId: number
  hasThumb: boolean
  headlineOffer?: { id: number } | null
}

function renderOfferHeadlineCard({
  offerId,
  hasThumb,
  headlineOffer = null,
}: RenderOptions) {
  vi.spyOn(HeadlineOfferContext, 'useHeadlineOfferContext').mockReturnValue({
    headlineOffer,
    upsertHeadlineOffer: mockUpsertHeadlineOffer,
    removeHeadlineOffer: mockRemoveHeadlineOffer,
    isHeadlineOfferAllowedForOfferer: true,
  } as any)

  return renderWithProviders(
    <OfferHeadlineCard offerId={offerId} hasThumb={hasThumb} />,
    {
      storeOverrides: {
        user: {
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
      },
    }
  )
}

describe('OfferHeadlineCard', () => {
  describe('when the offer is already the headline offer', () => {
    it('should display the correct text and button', () => {
      renderOfferHeadlineCard({
        offerId: 1,
        hasThumb: true,
        headlineOffer: { id: 1 },
      })

      expect(screen.getByText('Votre offre est à la une')).toBeInTheDocument()
      expect(
        screen.getByText(
          'Elle est mise en avant et affichée en priorité sur votre page dans l’application'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Ne plus mettre à la une' })
      ).toBeInTheDocument()
    })

    it('should call removeHeadlineOffer when clicking the button', async () => {
      renderOfferHeadlineCard({
        offerId: 1,
        hasThumb: true,
        headlineOffer: { id: 1 },
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Ne plus mettre à la une' })
      )

      expect(mockRemoveHeadlineOffer).toHaveBeenCalledTimes(1)
    })
  })

  describe('when another offer is the headline offer', () => {
    it('should display the correct text and button', () => {
      renderOfferHeadlineCard({
        offerId: 1,
        hasThumb: true,
        headlineOffer: { id: 2 },
      })

      expect(
        screen.getByText(
          'Ne laissez pas votre offre passer inaperçue : passez-la à la une'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Mettre l’offre à la une' })
      ).toBeInTheDocument()
    })

    it('should open the confirmation dialog when clicking the button', async () => {
      renderOfferHeadlineCard({
        offerId: 1,
        hasThumb: true,
        headlineOffer: { id: 2 },
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Mettre l’offre à la une' })
      )

      expect(
        screen.getByText(
          'Vous êtes sur le point de remplacer votre offre à la une par une nouvelle offre.'
        )
      ).toBeInTheDocument()
    })

    it('should call upsertHeadlineOffer when confirming replacement', async () => {
      renderOfferHeadlineCard({
        offerId: 1,
        hasThumb: true,
        headlineOffer: { id: 2 },
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Mettre l’offre à la une' })
      )
      await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))

      expect(mockUpsertHeadlineOffer).toHaveBeenCalledWith({
        offerId: 1,
        context: { actionType: 'replace' },
      })
    })
  })

  describe('when there is no headline offer', () => {
    describe('and the offer has a thumbnail', () => {
      it('should display the correct text and button', () => {
        renderOfferHeadlineCard({
          offerId: 1,
          hasThumb: true,
          headlineOffer: null,
        })

        expect(
          screen.getByText(
            'Ne laissez pas votre offre passer inaperçue : passez-la à la une'
          )
        ).toBeInTheDocument()
        expect(
          screen.getByRole('button', { name: 'Mettre l’offre à la une' })
        ).toBeInTheDocument()
      })

      it('should call upsertHeadlineOffer directly when clicking the button', async () => {
        renderOfferHeadlineCard({
          offerId: 1,
          hasThumb: true,
          headlineOffer: null,
        })

        await userEvent.click(
          screen.getByRole('button', { name: 'Mettre l’offre à la une' })
        )

        expect(mockUpsertHeadlineOffer).toHaveBeenCalledWith({
          offerId: 1,
          context: {
            actionType: 'add',
            requiredImageUpload: true,
          },
        })
      })
    })

    describe('and the offer does not have a thumbnail', () => {
      it('should open the HeadlineOfferImageDialogs when clicking the button', async () => {
        renderOfferHeadlineCard({
          offerId: 1,
          hasThumb: false,
          headlineOffer: null,
        })

        expect(screen.getByText('Dialog Closed')).toBeInTheDocument()

        await userEvent.click(
          screen.getByRole('button', { name: 'Mettre l’offre à la une' })
        )

        expect(screen.getByText('Dialog Open')).toBeInTheDocument()
        expect(mockUpsertHeadlineOffer).not.toHaveBeenCalled()
      })
    })
  })
})
