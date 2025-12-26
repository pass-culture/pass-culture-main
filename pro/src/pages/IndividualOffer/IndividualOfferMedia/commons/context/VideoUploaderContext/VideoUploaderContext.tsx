import {
  createContext,
  type Dispatch,
  type SetStateAction,
  useCallback,
  useContext,
  useState,
} from 'react'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModel, VideoData } from '@/apiClient/v1'
import { noop } from '@/commons/utils/noop'

type VideoUploaderContextValues = {
  setVideoUrl: Dispatch<SetStateAction<string | null | undefined>>
  videoData?: VideoData
  handleVideoOnSubmit: () => Promise<GetIndividualOfferResponseModel>
  onVideoUpload: (p: onVideoUploadProps) => void
  onVideoDelete: () => void
  videoUrl?: string | null
  offerId?: number
}

const VideoUploaderContext = createContext<VideoUploaderContextValues>({
  setVideoUrl: noop,
  videoData: undefined,
  // biome-ignore lint/suspicious/useAwait:  default values
  handleVideoOnSubmit: async () => {
    throw new Error('VideoUploaderContext not provided')
  },
  onVideoUpload: noop,
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
}: VideoUploaderContextProviderProps) {
  const [videoUrl, setVideoUrl] = useState(initialVideoData?.videoUrl)
  const [videoData, setVideoData] = useState(initialVideoData)

  const onVideoUpload = async ({ onSuccess, onError }: onVideoUploadProps) => {
    if (videoUrl) {
      try {
        const response = await api.getOfferVideoMetadata(videoUrl)
        setVideoData(response)
        onSuccess()
      } catch (error) {
        const humanError = getHumanReadableApiError(error)
        onError(humanError)
      }
    }
  }

  const onVideoDelete = () => {
    setVideoUrl(undefined)
    setVideoData(undefined)
  }

  const handleVideoOnSubmit = useCallback(async () => {
    return await api.patchOffer(offerId, {
      videoUrl: videoUrl ?? '',
    })
  }, [videoUrl, offerId])

  return (
    <VideoUploaderContext.Provider
      value={{
        videoUrl,
        videoData,
        handleVideoOnSubmit,
        setVideoUrl,
        onVideoUpload,
        onVideoDelete,
        offerId,
      }}
    >
      {children}
    </VideoUploaderContext.Provider>
  )
}
