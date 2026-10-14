import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import { ApiError } from '@/apiClient/compat'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  useVideoUploaderContext,
  VideoUploaderContextProvider,
} from './VideoUploaderContext'

const LABELS = {
  display: {
    input: 'Test input url',
    description: 'Test video description',
  },
  controls: {
    delete: 'delete',
    upload: 'upload',
    submit: 'submit',
  },
}

const TestComponent = () => {
  const {
    videoUrl,
    videoData,
    handleVideoOnSubmit,
    videoDescription,
    onVideoUpload,
    onVideoDelete,
  } = useVideoUploaderContext()
  const [draftVideoUrl, setDraftVideoUrl] = useState(videoUrl)
  const [draftVideoDescription, setDraftVideoDescription] =
    useState(videoDescription)

  return (
    <>
      <h1>Test Component</h1>
      <label>
        {LABELS.display.input}
        <input
          type="text"
          value={draftVideoUrl}
          onChange={(e) => setDraftVideoUrl(e.target.value)}
        />
      </label>
      <p>Video url: {videoUrl}</p>
      <label>
        {LABELS.display.description}
        <input
          type="text"
          value={draftVideoDescription}
          onChange={(e) => setDraftVideoDescription(e.target.value)}
        />
      </label>
      <p>Video description: {videoDescription}</p>
      <div>
        <p>{videoData?.videoDuration} min</p>
        <p>{videoData?.videoThumbnailUrl}</p>
        <p>{videoData?.videoTitle}</p>
      </div>
      <button type="button" onClick={onVideoDelete}>
        {LABELS.controls.delete}
      </button>
      <button
        type="button"
        onClick={async () =>
          await onVideoUpload({
            videoUrl: draftVideoUrl,
            videoDescription: draftVideoDescription,
            onSuccess: vi.fn(),
            onError: vi.fn(),
          })
        }
      >
        {LABELS.controls.upload}
      </button>
      <button type="button" onClick={handleVideoOnSubmit}>
        {LABELS.controls.submit}
      </button>
    </>
  )
}

const renderVideoUploaderContext = (offer: GetIndividualOfferResponseModel) => {
  return renderWithProviders(
    <VideoUploaderContextProvider
      initialVideoData={offer.videoData}
      offerId={offer.id}
    >
      <TestComponent />
    </VideoUploaderContextProvider>
  )
}

describe('VideoUploaderContext', () => {
  it('should render without accessibility violations', async () => {
    const offer = getIndividualOfferFactory({
      videoData: {
        videoDuration: 3,
        videoThumbnailUrl: 'http://youtube.image.com',
        videoTitle: 'Ma super vidéo',
        videoUrl: 'http://youtube.url',
      },
    })
    const { container } = renderVideoUploaderContext(offer)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render component with offer values', () => {
    const offer = getIndividualOfferFactory({
      videoData: {
        videoDuration: 3,
        videoThumbnailUrl: 'http://youtube.image.com',
        videoTitle: 'Ma super vidéo',
        videoUrl: 'http://youtube.url',
      },
    })

    renderVideoUploaderContext(offer)

    expect(screen.getByText('3 min')).toBeInTheDocument()
    expect(screen.getByText('http://youtube.image.com')).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(screen.getByLabelText(LABELS.display.input)).toHaveValue(
      'http://youtube.url'
    )
    expect(
      screen.getByText('Video url: http://youtube.url')
    ).toBeInTheDocument()
  })

  it('should clear values on click on delele', async () => {
    const offer = getIndividualOfferFactory({
      videoData: {
        videoDuration: 3,
        videoThumbnailUrl: 'http://youtube.image.com',
        videoTitle: 'Ma super vidéo',
        videoUrl: 'http://youtube.url',
        videoDescription: 'Description initiale',
      },
    })

    renderVideoUploaderContext(offer)

    await userEvent.click(screen.getByText(LABELS.controls.delete))

    expect(screen.queryByText('3 min')).not.toBeInTheDocument()
    expect(
      screen.queryByText('http://youtube.image.com')
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Ma super vidéo')).not.toBeInTheDocument()
    expect(
      screen.queryByText('Video url: http://youtube.url')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Video description: Description initiale')
    ).not.toBeInTheDocument()
  })

  it('should upload new data on click on update', async () => {
    vi.spyOn(api, 'getOfferVideoMetadata').mockResolvedValue({
      videoDuration: 3,
      videoThumbnailUrl: 'http://youtube.image.com',
      videoTitle: 'Ma super vidéo',
      videoUrl: 'http://youtube.url',
    })

    const offer = getIndividualOfferFactory({
      videoData: {},
    })

    renderVideoUploaderContext(offer)

    await userEvent.type(
      screen.getByLabelText(LABELS.display.input),
      'http://youtube.url'
    )
    await userEvent.click(screen.getByText(LABELS.controls.upload))

    expect(api.getOfferVideoMetadata).toHaveBeenCalledWith({
      query: { videoUrl: 'http://youtube.url' },
    })
    expect(screen.getByText('3 min')).toBeInTheDocument()
    expect(screen.getByText('http://youtube.image.com')).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(
      screen.getByText('Video url: http://youtube.url')
    ).toBeInTheDocument()
  })

  it('should update offer on click on submit with the previewed url', async () => {
    vi.spyOn(api, 'getOfferVideoMetadata').mockResolvedValue({
      videoUrl: 'http://youtube.url',
    })
    vi.spyOn(api, 'updateOfferVideo').mockResolvedValue({})

    const offer = getIndividualOfferFactory({
      videoData: {},
    })

    renderVideoUploaderContext(offer)

    await userEvent.type(
      screen.getByLabelText(LABELS.display.input),
      'http://youtube.url'
    )
    await userEvent.click(screen.getByText(LABELS.controls.upload))
    await userEvent.click(screen.getByText(LABELS.controls.submit))

    expect(api.updateOfferVideo).toHaveBeenCalledWith({
      path: { offer_id: offer.id },
      body: {
        videoUrl: 'http://youtube.url',
      },
    })
  })

  it('should not submit an url nor a description which preview has failed', async () => {
    vi.spyOn(api, 'getOfferVideoMetadata').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        { status: 400, body: { videoUrl: 'api error' } } as ApiResult,
        ''
      )
    )
    vi.spyOn(api, 'updateOfferVideo').mockResolvedValue({})

    const offer = getIndividualOfferFactory({
      videoData: {
        videoUrl: 'http://youtube.url',
        videoDescription: 'Description initiale',
      },
    })

    renderVideoUploaderContext(offer)

    const input = screen.getByLabelText(LABELS.display.input)
    await userEvent.clear(input)
    await userEvent.type(input, 'http://invalid.youtube.url')
    const description = screen.getByLabelText(LABELS.display.description)
    await userEvent.clear(description)
    await userEvent.type(description, 'Nouvelle description')
    await userEvent.click(screen.getByText(LABELS.controls.upload))
    await userEvent.click(screen.getByText(LABELS.controls.submit))

    expect(api.getOfferVideoMetadata).toHaveBeenCalledWith({
      query: { videoUrl: 'http://invalid.youtube.url' },
    })
    expect(
      screen.getByText('Video url: http://youtube.url')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Video description: Description initiale')
    ).toBeInTheDocument()
    expect(api.updateOfferVideo).toHaveBeenCalledWith({
      path: { offer_id: offer.id },
      body: {
        videoUrl: 'http://youtube.url',
        videoDescription: 'Description initiale',
      },
    })
  })

  it('should submit the updated video description once previewed', async () => {
    vi.spyOn(api, 'getOfferVideoMetadata').mockResolvedValue({
      videoUrl: 'http://youtube.url',
    })
    vi.spyOn(api, 'updateOfferVideo').mockResolvedValue({})

    const offer = getIndividualOfferFactory({
      videoData: {
        videoUrl: 'http://youtube.url',
        videoDescription: 'Description initiale',
      },
    })

    renderVideoUploaderContext(offer)

    const description = screen.getByLabelText(LABELS.display.description)
    expect(description).toHaveValue('Description initiale')

    await userEvent.clear(description)
    await userEvent.type(description, 'Nouvelle description')

    expect(
      screen.getByText('Video description: Description initiale')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText(LABELS.controls.upload))
    await userEvent.click(screen.getByText(LABELS.controls.submit))

    expect(
      screen.getByText('Video description: Nouvelle description')
    ).toBeInTheDocument()
    expect(api.updateOfferVideo).toHaveBeenCalledWith({
      path: { offer_id: offer.id },
      body: {
        videoUrl: 'http://youtube.url',
        videoDescription: 'Nouvelle description',
      },
    })
  })
})
