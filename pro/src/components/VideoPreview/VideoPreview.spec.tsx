import { screen } from '@testing-library/react'

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

  it('does not render an empty caption when no description is provided', () => {
    renderWithProviders(
      <VideoPreview videoThumbnailUrl="http://youtube.image.com" />
    )

    expect(document.querySelector('figcaption')).not.toBeInTheDocument()
  })
})
