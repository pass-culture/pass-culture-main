import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ApiError } from '@/apiClient/adage'
import type { ApiRequestOptions } from '@/apiClient/adage/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { VideoUploaderContextProvider } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'

import { ModalVideo } from './ModalVideo'

const mockLogEvent = vi.fn()

describe('ModalVideo', () => {
  it('should render an heading, a cancel button, a save button and a field', () => {
    renderWithProviders(<ModalVideo open={true} />)

    waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter une vidéo' })
      ).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ajouter' })).toBeInTheDocument()
    expect(screen.getByLabelText('Lien URL Youtube')).toBeInTheDocument()
  })

  it('should display error and log wrong url', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const offer = getIndividualOfferFactory({
      videoData: {},
    })

    renderWithProviders(
      <VideoUploaderContextProvider
        offerId={offer.id}
        initialVideoData={offer.videoData}
      >
        <ModalVideo open={true} />
      </VideoUploaderContextProvider>
    )

    waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter une vidéo' })
      ).toBeInTheDocument()
    })

    await userEvent.type(screen.getByLabelText('Lien URL Youtube'), 'fake url')
    await userEvent.tab()

    expect(
      screen.getByText(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )
    ).toBeInTheDocument()
    expect(mockLogEvent).toHaveBeenCalled()
  })

  it('should display api error', async () => {
    vi.spyOn(api, 'getOfferVideoMetadata').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            videoUrl: 'api error',
          },
        } as ApiResult,
        ''
      )
    )

    const offer = getIndividualOfferFactory({
      videoData: {},
    })

    renderWithProviders(
      <VideoUploaderContextProvider
        offerId={offer.id}
        initialVideoData={offer.videoData}
      >
        <ModalVideo open={true} />
      </VideoUploaderContextProvider>
    )

    waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter une vidéo' })
      ).toBeInTheDocument()
    })

    await userEvent.type(
      screen.getByLabelText('Lien URL Youtube'),
      'https://www.youtube.com/watch?v=25ztioI37oc'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Ajouter' }))

    expect(screen.getByText('api error')).toBeInTheDocument()
  })

  it('should get video meta data on click on "Ajouter"', async () => {
    vi.spyOn(api, 'getOfferVideoMetadata').mockResolvedValue({
      videoDuration: 3,
      videoThumbnailUrl: 'http://youtube.image.com',
      videoTitle: 'Ma super vidéo',
      videoUrl: 'http://youtube.url',
    })

    const offer = getIndividualOfferFactory({
      videoData: {},
    })

    renderWithProviders(
      <VideoUploaderContextProvider
        offerId={offer.id}
        initialVideoData={offer.videoData}
      >
        <ModalVideo open={true} />
      </VideoUploaderContextProvider>
    )

    waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter une vidéo' })
      ).toBeInTheDocument()
    })

    await userEvent.type(
      screen.getByLabelText('Lien URL Youtube'),
      'https://www.youtube.com/watch?v=25ztioI37oc'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Ajouter' }))

    expect(api.getOfferVideoMetadata).toHaveBeenCalled()
  })
})
