import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { MediaSection, type MediaSectionProps } from './MediaSection'

const renderMediaSection = (props: Partial<MediaSectionProps> = {}) => {
  const finalProps = {
    ...MOCK_DATA,
    ...props,
  }
  return renderWithProviders(<MediaSection {...finalProps} />, {
    storeOverrides: {
      user: {
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    },
  })
}

const MOCK_DATA = {
  offerId: 0,
  imageUrl: 'http://localhost/storage/thumbs/mediations/ABAC',
  imageCredit: 'Photo de Camille Doe',
  videoUrl: 'https://www.youtube.com/watch?v=0R5PZxOgoz8',
}

const LABELS = {
  title: 'Image et vidéo',
  editLink: 'Modifier l’image et la vidéo de l’offre',
  imageSubSectionTitle: 'Ajoutez une image',
  imageSubSectionImageAlt: 'Prévisualisation de l’image',
  imageCredit: `Crédit image : ${MOCK_DATA.imageCredit}`,
  imageFallbackText: 'Pas d’image',
  videoSubSectionTitle: 'Ajoutez une vidéo',
}

describe('MediaSection', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderMediaSection()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should always render a title and an edit link', () => {
    renderMediaSection()

    const title = screen.getByRole('heading', { name: LABELS.title })
    expect(title).toBeInTheDocument()
    const editLink = screen.getByRole('link', { name: LABELS.editLink })
    expect(editLink).toBeInTheDocument()
    expect(editLink).toHaveAttribute(
      'href',
      `/offre/individuelle/${MOCK_DATA.offerId}/edition/media`
    )
  })

  describe('about image', () => {
    it('preserves the alternative text and associates the image with its credit', () => {
      renderMediaSection({
        imageAlternativeText: 'Une scène de théâtre',
      })

      const image = screen.getByRole('img', {
        name: 'Une scène de théâtre',
      })
      expect(image).toHaveAccessibleDescription(LABELS.imageCredit)
      expect(image.closest('figure')).toContainElement(
        screen.getByText(LABELS.imageCredit).closest('figcaption')
      )
    })

    it('should render an image subsection with provided data by default', () => {
      renderMediaSection()

      const imageSubSection = screen.getByRole('heading', {
        name: LABELS.imageSubSectionTitle,
      })
      expect(imageSubSection).toBeInTheDocument()
      const image = screen.getByRole('img', {
        name: LABELS.imageSubSectionImageAlt,
      })
      expect(image).toBeInTheDocument()
      expect(image).toHaveAttribute('src', MOCK_DATA.imageUrl)
      expect(screen.getByText(LABELS.imageCredit)).toBeInTheDocument()
    })

    it('should not render an image credit when no credit is provided', () => {
      renderMediaSection({ imageCredit: '' })

      expect(screen.queryByText(/Crédit image\s*:/)).not.toBeInTheDocument()
    })

    it('should not render any image subsection when asked (shouldImageBeHidden)', () => {
      renderMediaSection({ isOnCreation: true })

      const imageSubSection = screen.queryByRole('heading', {
        name: LABELS.imageSubSectionTitle,
      })
      expect(imageSubSection).not.toBeInTheDocument()
    })

    it('should render a fallback text when no image is provided', () => {
      renderMediaSection({ imageUrl: undefined })

      const image = screen.queryByRole('img', {
        name: LABELS.imageSubSectionImageAlt,
      })
      expect(image).not.toBeInTheDocument()
      const imageFallback = screen.getByText(LABELS.imageFallbackText)
      expect(imageFallback).toBeInTheDocument()
    })
  })

  describe('about video', () => {
    it.each([false, true])(
      'renders the saved description associated with the preview (creation: %s)',
      (isOnCreation) => {
        renderMediaSection({
          isOnCreation,
          videoData: {
            videoUrl: MOCK_DATA.videoUrl,
            videoThumbnailUrl: 'http://youtube.image.com',
            videoDescription: 'Description enregistrée',
          },
        })

        const image = screen.getByRole('img', {
          name: 'Prévisualisation de la vidéo',
        })
        expect(image).toHaveAccessibleDescription(
          'Description textuelle de la vidéo : Description enregistrée'
        )
        expect(
          screen.getByText(/Description enregistrée/).closest('figcaption')
        ).toBeInTheDocument()
        expect(
          screen.queryByText(
            'Aucune description textuelle renseignée pour la vidéo'
          )
        ).not.toBeInTheDocument()
      }
    )

    it('renders the saved description even when the thumbnail is unavailable', () => {
      renderMediaSection({
        videoData: {
          videoUrl: MOCK_DATA.videoUrl,
          videoDescription: 'Description enregistrée',
        },
      })

      expect(screen.getByText(MOCK_DATA.videoUrl)).toBeInTheDocument()
      expect(
        screen.getByText('Description textuelle de la vidéo :')
      ).toBeInTheDocument()
      expect(screen.getByText('Description enregistrée')).toBeInTheDocument()
    })

    it('should render a video subsection with provided data', () => {
      renderMediaSection({ videoData: { videoUrl: MOCK_DATA.videoUrl } })

      const videoSubSection = screen.getByRole('heading', {
        name: LABELS.videoSubSectionTitle,
      })
      expect(videoSubSection).toBeInTheDocument()
      const videoUrl = screen.getByText(MOCK_DATA.videoUrl)
      expect(videoUrl).toBeInTheDocument()
    })

    it('should render a fallback "-" text when no videoUrl is provided', () => {
      renderMediaSection({ videoData: { videoUrl: undefined } })

      const videoUrl = screen.getByText('-')
      expect(videoUrl).toBeInTheDocument()
    })
  })
})
