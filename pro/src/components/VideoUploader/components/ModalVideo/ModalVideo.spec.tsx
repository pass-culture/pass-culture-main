import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import { ApiError } from '@/apiClient/compat'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { VideoUploaderContextProvider } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'

import { ModalVideo } from './ModalVideo'

const mockLogEvent = vi.fn()

describe('ModalVideo', () => {
  it('should render an heading, a cancel button, a save button and a field', () => {
    renderWithProviders(
      <ModalVideo
        isOpen={true}
        onClose={() => {}}
        addVideoRef={{ current: null }}
        editVideoRef={{ current: null }}
      />
    )

    waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter une vidéo' })
      ).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ajouter' })).toBeInTheDocument()
    expect(screen.getByLabelText('Lien URL Youtube')).toBeInTheDocument()
  })

  it('should show the video description field when the checkbox is checked', async () => {
    const offer = getIndividualOfferFactory({ videoData: {} })

    renderWithProviders(
      <VideoUploaderContextProvider
        offerId={offer.id}
        initialVideoData={offer.videoData}
      >
        <ModalVideo
          isOpen={true}
          onClose={() => {}}
          addVideoRef={{ current: null }}
          editVideoRef={{ current: null }}
        />
      </VideoUploaderContextProvider>
    )

    const checkbox = screen.getByRole('checkbox', {
      name: /^Ajouter une description textuelle détaillée/,
    })
    expect(checkbox).not.toBeChecked()
    expect(
      screen.queryByRole('textbox', {
        name: /^Description textuelle pour les malvoyants/,
      })
    ).not.toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(checkbox).toBeChecked()
    const description = screen.getByRole('textbox', {
      name: /^Description textuelle pour les malvoyants/,
    })
    await userEvent.type(description, 'Description de la vidéo')
    expect(description).toHaveValue('Description de la vidéo')

    await userEvent.click(checkbox)
    expect(
      screen.queryByRole('textbox', {
        name: /^Description textuelle pour les malvoyants/,
      })
    ).not.toBeInTheDocument()

    await userEvent.click(checkbox)
    expect(
      screen.getByRole('textbox', {
        name: /^Description textuelle pour les malvoyants/,
      })
    ).toHaveValue('')
  })

  it('should show and clear the existing video description when editing a video', async () => {
    const offer = getIndividualOfferFactory({
      videoData: { videoDescription: 'Description existante' },
    })

    renderWithProviders(
      <VideoUploaderContextProvider
        offerId={offer.id}
        initialVideoData={offer.videoData}
      >
        <ModalVideo
          isOpen={true}
          onClose={() => {}}
          addVideoRef={{ current: null }}
          editVideoRef={{ current: null }}
        />
      </VideoUploaderContextProvider>
    )

    expect(
      screen.getByRole('checkbox', {
        name: /^Ajouter une description textuelle détaillée/,
      })
    ).toBeChecked()
    expect(
      screen.getByRole('textbox', {
        name: /^Description textuelle pour les malvoyants/,
      })
    ).toHaveValue('Description existante')

    const checkbox = screen.getByRole('checkbox', {
      name: /^Ajouter une description textuelle détaillée/,
    })
    await userEvent.click(checkbox)
    await userEvent.click(checkbox)

    expect(
      screen.getByRole('textbox', {
        name: /^Description textuelle pour les malvoyants/,
      })
    ).toHaveValue('')
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
        <ModalVideo
          isOpen={true}
          onClose={() => {}}
          addVideoRef={{ current: null }}
          editVideoRef={{ current: null }}
        />
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
        <ModalVideo
          isOpen={true}
          onClose={() => {}}
          addVideoRef={{ current: null }}
          editVideoRef={{ current: null }}
        />
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
        <ModalVideo
          isOpen={true}
          onClose={() => {}}
          addVideoRef={{ current: null }}
          editVideoRef={{ current: null }}
        />
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
