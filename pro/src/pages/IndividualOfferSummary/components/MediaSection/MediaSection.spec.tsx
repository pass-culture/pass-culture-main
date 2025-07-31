import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { MediaSection, MediaSectionProps } from './MediaSection'

const renderMediaSection = (props: Partial<MediaSectionProps> = {}) => {
  const finalProps = {
    ...MOCK_DATA,
    ...props,
  }
  return renderWithProviders(<MediaSection {...finalProps} />)
}

const MOCK_DATA = {
  offerId: 0,
  imageUrl: 'http://localhost/storage/thumbs/mediations/ABAC',
  videoUrl: 'https://www.youtube.com/watch?v=0R5PZxOgoz8',
}

const LABELS = {
  title: 'Image et vidéo',
  editLink: 'Modifier les détails de l’offre',
  imageSubSectionTitle: 'Ajoutez une image',
  imageSubSectionImageAlt: 'Prévisualisation de l’image',
  imageFallbackText: 'Pas d’image',
  videoSubSectionTitle: 'Ajoutez une vidéo',
}

describe('MediaSection', () => {
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
    })

    it('should not render any image subsection when asked (shouldImageBeHidden)', () => {
      renderMediaSection({ shouldImageBeHidden: true })

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
    it('should render a video subsection with provided data', () => {
      renderMediaSection()

      const videoSubSection = screen.getByRole('heading', {
        name: LABELS.videoSubSectionTitle,
      })
      expect(videoSubSection).toBeInTheDocument()
      const videoUrl = screen.getByText(MOCK_DATA.videoUrl)
      expect(videoUrl).toBeInTheDocument()
    })

    it('should render a fallback "-" text when no videoUrl is provided', () => {
      renderMediaSection({ videoUrl: undefined })

      const videoUrl = screen.getByText('-')
      expect(videoUrl).toBeInTheDocument()
    })
  })
})
