import {
  createContext,
  type Dispatch,
  type SetStateAction,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'

import { apiNew } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type {
  GetIndividualOfferWithAddressResponseModel,
  VideoData,
} from '@/apiClient/v1/new'
import { noop, noopAsync } from '@/commons/utils/noop'

type VideoUploaderContextValues = {
  setVideoUrl: Dispatch<SetStateAction<string | undefined>>
  videoData?: VideoData
  handleVideoOnSubmit: () => Promise<GetIndividualOfferWithAddressResponseModel>
  onVideoUpload: (p: onVideoUploadProps) => Promise<void>
  onVideoDelete: () => void
  videoUrl?: string
  offerId?: number
}

const VideoUploaderContext = createContext<VideoUploaderContextValues>({
  setVideoUrl: noop,
  videoData: undefined,
  // biome-ignore lint/suspicious/useAwait:  default values
  handleVideoOnSubmit: async () => {
    throw new Error('VideoUploaderContext not provided')
  },
  onVideoUpload: noopAsync,
  onVideoDelete: noop,
  offerId: undefined,
})

export const useVideoUploaderContext = () => {
  return useContext(VideoUploaderContext)
}

type VideoUploaderContextProviderProps = {
  children: React.ReactNode
  offerId: number
  initialVideoData?: VideoData
}

type onVideoUploadProps = {
  onSuccess: () => void
  onError: Dispatch<SetStateAction<string | undefined>>
}

export function VideoUploaderContextProvider({
  children,
  initialVideoData,
  offerId,
}: Readonly<VideoUploaderContextProviderProps>) {
  const [videoUrl, setVideoUrl] = useState(initialVideoData?.videoUrl)
  const [videoData, setVideoData] = useState(initialVideoData)

  const onVideoUpload = useCallback(
    async ({ onSuccess, onError }: onVideoUploadProps) => {
      if (videoUrl) {
        try {
          const response = await apiNew.getOfferVideoMetadata({
            query: { videoUrl },
          })
          setVideoData(response)
          onSuccess()
        } catch (error) {
          const humanError = getHumanReadableApiError(error)
          onError(humanError)
        }
      }
    },
    [videoUrl]
  )

  const onVideoDelete = useCallback(() => {
    setVideoUrl(undefined)
    setVideoData(undefined)
  }, [])

  const handleVideoOnSubmit = useCallback(async () => {
    return await apiNew.patchOffer({
      path: { offer_id: offerId },
      body: {
        videoUrl: videoUrl ?? '',
      },
    })
  }, [videoUrl, offerId])

  const contextValue = useMemo(
    () => ({
      videoUrl,
      videoData,
      handleVideoOnSubmit,
      setVideoUrl,
      onVideoUpload,
      onVideoDelete,
      offerId,
    }),
    [
      videoUrl,
      videoData,
      handleVideoOnSubmit,
      onVideoUpload,
      onVideoDelete,
      offerId,
    ]
  )

  return (
    <VideoUploaderContext.Provider value={contextValue}>
      {children}
    </VideoUploaderContext.Provider>
  )
}
