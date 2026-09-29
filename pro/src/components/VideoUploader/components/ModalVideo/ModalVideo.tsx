import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { useVideoUploaderContext } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'
import { getUrlYoutubeError } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/getUrlYoutubeError'

import youtubeLogo from './assets/youtube-logo.png'
import styles from './ModalVideo.module.scss'

interface ModalVideoProps {
  isOpen: boolean
  onClose: () => void
  editVideoRef: React.RefObject<HTMLElement | null>
  addVideoRef: React.RefObject<HTMLElement | null>
}

export const ModalVideo = ({
  isOpen,
  onClose,
  editVideoRef,
  addVideoRef,
}: ModalVideoProps): JSX.Element | null => {
  const [error, setError] = useState<string>()
  const {
    videoUrl,
    videoData,
    onVideoUpload,
    setVideoUrl,
    offerId,
    videoDescription,
    setVideoDescription,
  } = useVideoUploaderContext()
  const [isInformative, setIsInformative] = useState(Boolean(videoDescription))
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
      refToFocusOnClose={
        videoData?.videoThumbnailUrl ? editVideoRef : addVideoRef
      }
    >
      <div className={styles['modal-video']}>
        <div className={styles['modal-video-content']}>
          <img
            alt=""
            aria-hidden
            width="70px"
            height="17px"
            src={youtubeLogo}
          />
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
          <div className={styles['video-description']}>
            <Checkbox
              label="Ajouter une description textuelle détaillée"
              description="Permet aux personnes malvoyantes de prendre connaissance du contexte de la vidéo sous forme de texte."
              variant="detailed"
              checked={isInformative}
              onChange={(e) => {
                setIsInformative(e.target.checked)
                if (!e.target.checked) {
                  setVideoDescription('')
                }
              }}
              collapsed={
                <TextInput
                  label="Description textuelle pour les malvoyants"
                  name="alternativeText"
                  maxCharactersCount={150}
                  value={videoDescription ?? ''}
                  required
                  onChange={(e) => setVideoDescription(e.target.value)}
                />
              }
            />
          </div>
        </div>
      </div>
    </DetailedModal>
  )
}
