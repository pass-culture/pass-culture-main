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
      />
    )

    expect(
      screen.getByRole('img', { name: 'Prévisualisation de l’image' })
    ).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(screen.getByText('3 min')).toBeInTheDocument()
  })
})
