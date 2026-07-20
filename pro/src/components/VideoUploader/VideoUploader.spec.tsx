import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { VenueState } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { VideoUploaderContextProvider } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'

import { VideoUploader } from './VideoUploader'

const selectedPartnerVenue = makeGetVenueResponseModel({ id: 1 })
const defaultStoreOverrides = {
  user: {
    currentUser: sharedCurrentUserFactory(),
    selectedPartnerVenue,
  },
}

describe('VideoUploader', () => {
  it('should render a button and a text when no video has been provided', () => {
    renderWithProviders(<VideoUploader />, {
      storeOverrides: defaultStoreOverrides,
    })

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
      </VideoUploaderContextProvider>,
      { storeOverrides: defaultStoreOverrides }
    )

    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Supprimer' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('img', { name: 'Prévisualisation de l\u2019image' })
    ).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(screen.getByText('3 min')).toBeInTheDocument()
  })

  it('should open modal on click on add video button', async () => {
    renderWithProviders(<VideoUploader />, {
      storeOverrides: defaultStoreOverrides,
    })

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

  it('should disable form when venue is closed', () => {
    const closedVenue = makeGetVenueResponseModel({
      id: 1,
      state: VenueState.CLOSED,
    })

    renderWithProviders(<VideoUploader />, {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: closedVenue,
        },
      },
    })

    expect(
      screen.getByRole('button', { name: 'Ajouter une URL Youtube' })
    ).toBeDisabled()
  })
})
