import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { VideoUploaderContextProvider } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'

import { VideoUploader } from './VideoUploader'

describe('VideoUploader', () => {
  it('should render a button and a text when no video has been provided', () => {
    renderWithProviders(<VideoUploader />)

    expect(
      screen.getByRole('button', { name: 'Ajouter une URL Youtube' })
    ).toBeInTheDocument()

    expect(
      screen.getByText('Affichage de la prévisualisation ici')
    ).toBeInTheDocument()
  })

  it('should video meta data and action button when youtube url has been provided', () => {
    const offer = getIndividualOfferFactory({
      videoData: {
        videoDuration: 180,
        videoThumbnailUrl: 'http://youtube.image.com',
        videoTitle: 'Ma super vidéo',
      },
    })

    renderWithProviders(
      <VideoUploaderContextProvider
        offerId={offer.id}
        initialVideoData={offer.videoData}
      >
        <VideoUploader />
      </VideoUploaderContextProvider>
    )

    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Supprimer' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('img', { name: 'Prévisualisation de l’image' })
    ).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(screen.getByText('3 min')).toBeInTheDocument()
  })

  it('should open modal on click on add video button', async () => {
    renderWithProviders(<VideoUploader />)

    await userEvent.click(
      await screen.findByRole('button', {
        name: /Ajouter une URL Youtube/,
      })
    )
    expect(
      await screen.findByRole('heading', {
        name: /Ajouter une vidéo/,
      })
    ).toBeInTheDocument()
  })
})
