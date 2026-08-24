import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { useVideoUploaderContext } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'
import { getUrlYoutubeError } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/getUrlYoutubeError'

import youtubeLogo from './assets/youtube-logo.png'
import styles from './ModalVideo.module.scss'

interface ModalVideoProps {
  isOpen: boolean
  onClose: () => void
}

export const ModalVideo = ({
  isOpen,
  onClose,
}: ModalVideoProps): JSX.Element | null => {
  const [error, setError] = useState<string>()
  const { videoUrl, onVideoUpload, setVideoUrl, offerId } =
    useVideoUploaderContext()
  const { logEvent } = useAnalytics()

  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={onClose}
      title={`Ajouter une vidéo`}
      primaryAction={
        <Button
          onClick={async () => {
            if (videoUrl && !getUrlYoutubeError(videoUrl)) {
              await onVideoUpload({
                onSuccess: () => {
                  onClose()
                },
                onError: setError,
              })
            }
          }}
          label="Ajouter"
        />
      }
      secondaryAction={
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={onClose}
          label="Annuler"
        />
      }
      isFooterFixed
    >
      <div className={styles['modal-video']}>
        <div className={styles['modal-video-content']}>
          <img alt={''} width="70px" height="17px" src={youtubeLogo} />
          <TextInput
            name="videoUrl"
            label="Lien URL Youtube"
            description="Format : https://www.youtube.com/watch?v=0R5PZxOgoz8"
            error={error}
            value={videoUrl ?? ''}
            onBlur={(event) => {
              const value = event.target.value
              setError(getUrlYoutubeError(value))
              if (value && getUrlYoutubeError(value)) {
                logEvent(Events.OFFER_FORM_VIDEO_URL_ERROR, {
                  offerId: offerId,
                  videoUrl: value,
                })
              }
            }}
            onChange={(event) => {
              setVideoUrl(event.target.value)
            }}
          />
        </div>
      </div>
    </DetailedModal>
  )
}
