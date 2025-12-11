import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  useVideoUploaderContext,
  VideoUploaderContextProvider,
} from './VideoUploaderContext'

const LABELS = {
  display: {
    input: 'Test input url',
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
    setVideoUrl,
    onVideoUpload,
    onVideoDelete,
  } = useVideoUploaderContext()

  return (
    <>
      <h1>Test Component</h1>
      <label>
        {LABELS.display.input}
        <input
          type="text"
          value={videoUrl ?? ''}
          onChange={(e) => setVideoUrl(e.target.value)}
        />
      </label>
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
          await onVideoUpload({ onSuccess: vi.fn(), onError: vi.fn() })
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

const renderVideoUploaderContext = (
  offer: GetIndividualOfferWithAddressResponseModel
) => {
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
  })

  it('should clear values on click on delele', async () => {
    const offer = getIndividualOfferFactory({
      videoData: {
        videoDuration: 3,
        videoThumbnailUrl: 'http://youtube.image.com',
        videoTitle: 'Ma super vidéo',
        videoUrl: 'http://youtube.url',
      },
    })

    renderVideoUploaderContext(offer)

    await userEvent.click(screen.getByText(LABELS.controls.delete))

    expect(screen.queryByText('3 min')).not.toBeInTheDocument()
    expect(
      screen.queryByText('http://youtube.image.com')
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Ma super vidéo')).not.toBeInTheDocument()
    expect(screen.getByLabelText(LABELS.display.input)).toHaveValue('')
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

    expect(screen.getByText('3 min')).toBeInTheDocument()
    expect(screen.getByText('http://youtube.image.com')).toBeInTheDocument()
    expect(screen.getByText('Ma super vidéo')).toBeInTheDocument()
    expect(screen.getByLabelText(LABELS.display.input)).toHaveValue(
      'http://youtube.url'
    )
  })

  it('should update offer on click on submit', async () => {
    vi.spyOn(api, 'patchDraftOffer').mockResolvedValue(
      getIndividualOfferFactory()
    )

    const offer = getIndividualOfferFactory({
      videoData: {},
    })

    renderVideoUploaderContext(offer)

    await userEvent.type(
      screen.getByLabelText(LABELS.display.input),
      'http://youtube.url'
    )
    await userEvent.click(screen.getByText(LABELS.controls.submit))

    expect(api.patchDraftOffer).toBeCalledWith(offer.id, {
      videoUrl: 'http://youtube.url',
    })
  })
})
