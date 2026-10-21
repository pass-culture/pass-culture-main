import {
  createContext,
  type Dispatch,
  type SetStateAction,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { VideoDataV2 } from '@/apiClient/v1'
import { noop, noopAsync } from '@/commons/utils/noop'

type VideoUploaderContextValues = {
  videoDescription: string
  videoData?: VideoDataV2
  handleVideoOnSubmit: () => Promise<VideoDataV2>
  onVideoUpload: (p: onVideoUploadProps) => Promise<void>
  onVideoDelete: () => void
  videoUrl: string
  offerId?: number
}

const VideoUploaderContext = createContext<VideoUploaderContextValues>({
  videoData: undefined,
  videoDescription: '',
  videoUrl: '',
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
  initialVideoData?: VideoDataV2
}

type onVideoUploadProps = {
  videoUrl: string
  videoDescription: string
  onSuccess: () => void
  onError: Dispatch<SetStateAction<string | undefined>>
}

export function VideoUploaderContextProvider({
  children,
  initialVideoData,
  offerId,
}: Readonly<VideoUploaderContextProviderProps>) {
  const [videoUrl, setVideoUrl] = useState(initialVideoData?.videoUrl ?? '')
  const [videoDescription, setVideoDescription] = useState(
    initialVideoData?.videoDescription ?? ''
  )
  const [videoData, setVideoData] = useState(initialVideoData)

  const onVideoUpload = useCallback(
    async ({
      videoUrl,
      videoDescription,
      onSuccess,
      onError,
    }: onVideoUploadProps) => {
      if (videoUrl) {
        try {
          const response = await api.getOfferVideoMetadata({
            query: { videoUrl },
          })
          setVideoUrl(videoUrl)
          setVideoDescription(videoDescription)
          setVideoData(response)
          onSuccess()
        } catch (error) {
          const humanError = getHumanReadableApiError(error)
          onError(humanError)
        }
      }
    },
    []
  )

  const onVideoDelete = useCallback(() => {
    setVideoUrl('')
    setVideoDescription('')
    setVideoData(undefined)
  }, [])

  const handleVideoOnSubmit = useCallback(async () => {
    return await api.updateOfferVideo({
      path: { offer_id: offerId },
      body: {
        videoUrl,
        videoDescription: videoDescription || undefined,
      },
    })
  }, [videoUrl, offerId, videoDescription])

  const contextValue = useMemo(
    () => ({
      videoUrl,
      videoData,
      videoDescription,
      handleVideoOnSubmit,
      onVideoUpload,
      onVideoDelete,
      offerId,
    }),
    [
      videoUrl,
      videoData,
      videoDescription,
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
