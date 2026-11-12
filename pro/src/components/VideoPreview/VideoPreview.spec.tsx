import { fireEvent, screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VideoPreview } from './VideoPreview'

describe('VideoPreview', () => {
  it('should show preview', () => {
    renderWithProviders(
      <VideoPreview
        videoDuration={180}
        videoThumbnailUrl={'http://youtube.image.com'}
        videoTitle={'Ma super vidéo'}
        videoDescription={'Description de la vidéo'}
      />
    )

    expect(
      screen.getByRole('img', { name: 'Prévisualisation de la vidéo' })
    ).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(screen.getByText('3 min')).toBeInTheDocument()
    expect(
      screen.getByText(/Description de la vidéo/).closest('figcaption')
    ).toBeInTheDocument()
    expect(document.querySelectorAll('figure')).toHaveLength(1)
  })

  it('does render a placeholder caption when no description is provided', () => {
    renderWithProviders(
      <VideoPreview videoThumbnailUrl="http://youtube.image.com" />
    )

    expect(
      screen
        .getByText(/Aucune description textuelle renseignée pour la vidéo/)
        .closest('figcaption')
    ).toBeInTheDocument()
  })

  it('announces the video preview label when its thumbnail fails to load', () => {
    renderWithProviders(
      <VideoPreview videoThumbnailUrl="http://youtube.image.com" />
    )

    fireEvent.error(
      screen.getByRole('img', { name: 'Prévisualisation de la vidéo' })
    )

    expect(
      screen.getByRole('img', {
        name: 'Prévisualisation de la vidéo. Aperçu vidéo corrompu, veuillez ajouter une nouvelle vidéo',
      })
    ).toBeInTheDocument()
  })
})
