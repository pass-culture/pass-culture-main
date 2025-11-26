import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { useVideoUploaderContext } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'
import { getUrlYoutubeError } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/getUrlYoutubeError'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import {
  DialogBuilder,
  type DialogBuilderProps,
} from '@/ui-kit/DialogBuilder/DialogBuilder'

import youtubeLogo from './assets/youtube-logo.png'
import styles from './ModalVideo.module.scss'

interface ModalVideoProps extends Omit<DialogBuilderProps, 'children'> {}

export const ModalVideo = ({
  ...dialogBuilderProps
}: ModalVideoProps): JSX.Element | null => {
  const [error, setError] = useState<string>()
  const { videoUrl, onVideoUpload, setVideoUrl, offerId } =
    useVideoUploaderContext()
  const currentUser = useAppSelector(selectCurrentUser)
  const { logEvent } = useAnalytics()

  return (
    <DialogBuilder
      {...dialogBuilderProps}
      title="Ajouter une vidéo"
      imageTitle={<img alt={''} src={youtubeLogo} />}
      variant="drawer"
    >
      <div className={styles['modal-video']}>
        <div className={styles['modal-video-content']}>
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
                  userId: currentUser?.id,
                  videoUrl: value,
                })
              }
            }}
            onChange={(event) => {
              setVideoUrl(event.target.value)
            }}
          />
        </div>
        <DialogBuilder.Footer>
          <div className={styles['modal-video-footer']}>
            <Dialog.Close asChild>
              <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
            </Dialog.Close>
            <Button
              onClick={async () => {
                if (videoUrl && !getUrlYoutubeError(videoUrl)) {
                  await onVideoUpload({
                    onSuccess: () => {
                      dialogBuilderProps.onOpenChange?.(false)
                    },
                    onError: setError,
                  })
                }
              }}
            >
              Ajouter
            </Button>
          </div>
        </DialogBuilder.Footer>
      </div>
    </DialogBuilder>
  )
}
