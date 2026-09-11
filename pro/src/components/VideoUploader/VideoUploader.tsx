import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { isSelectedPartnerOrOffererClosed } from '@/commons/utils/isSelectedPartnerOrOffererClosed'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeVideoIcon from '@/icons/stroke-video.svg'
import { useVideoUploaderContext } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { VideoPreview } from '../VideoPreview/VideoPreview'
import { ModalVideo } from './components/ModalVideo/ModalVideo'
import styles from './VideoUploader.module.scss'

export const VideoUploader = () => {
  const [isOpen, setIsOpen] = useState(false)
  const { videoData, onVideoDelete } = useVideoUploaderContext()
  const { videoDuration, videoTitle, videoThumbnailUrl } = videoData ?? {}
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isClosed = isSelectedPartnerOrOffererClosed(selectedPartnerVenue)
  const editVideoRef = useRef<HTMLButtonElement>(null)
  const addVideoRef = useRef<HTMLButtonElement>(null)
  const hasVideo = !!videoThumbnailUrl
  // Adding or deleting a video swaps the whole "has video" / "no video" branch,
  // which unmounts the modal's dialog instead of letting it close gracefully —
  // so its own native close-focus-restore never runs. We manage focus ourselves
  // whenever this boolean flips, instead of relying on the dialog for that case.
  const hadVideoRef = useRef(hasVideo)

  useEffect(() => {
    if (hasVideo !== hadVideoRef.current) {
      if (hasVideo) {
        editVideoRef.current?.focus()
      } else {
        addVideoRef.current?.focus()
      }
    }
    hadVideoRef.current = hasVideo
  }, [hasVideo])

  const handleVideoDelete = () => {
    onVideoDelete()
  }

  return (
    <div className={styles['video-uploader-container']}>
      {videoThumbnailUrl ? (
        <>
          <VideoPreview
            videoDuration={videoDuration}
            videoTitle={videoTitle}
            videoThumbnailUrl={videoThumbnailUrl}
          />
          <div className={styles['action-wrapper']}>
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              icon={fullEditIcon}
              label="Modifier"
              onClick={() => setIsOpen(true)}
              disabled={isClosed}
              ref={editVideoRef}
            />
            <ModalVideo
              isOpen={isOpen}
              onClose={() => setIsOpen(false)}
              addVideoRef={addVideoRef}
              editVideoRef={editVideoRef}
            />
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              icon={fullTrashIcon}
              onClick={handleVideoDelete}
              label="Supprimer"
              disabled={isClosed}
            />
          </div>
        </>
      ) : (
        <div
          className={cn(styles['video-uploader-no-video'], {
            [styles['video-uploader-no-video-disabled']]: isClosed,
          })}
        >
          <SvgIcon src={strokeVideoIcon} alt="" width="44" />
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullMoreIcon}
            label="Ajouter une URL Youtube"
            onClick={() => setIsOpen(true)}
            disabled={isClosed}
            ref={addVideoRef}
          />
          <ModalVideo
            isOpen={isOpen}
            onClose={() => setIsOpen(false)}
            addVideoRef={addVideoRef}
            editVideoRef={editVideoRef}
          />
          <p className={styles['video-uploader-text-subtle']}>
            Affichage de la prévisualisation ici
          </p>
        </div>
      )}
    </div>
  )
}
