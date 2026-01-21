import { useState } from 'react'

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
            <ModalVideo
              onOpenChange={setIsOpen}
              open={isOpen}
              trigger={
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  size={ButtonSize.SMALL}
                  icon={fullEditIcon}
                  label="Modifier"
                />
              }
            />
            <Button
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullTrashIcon}
              onClick={onVideoDelete}
              label="Supprimer"
            />
          </div>
        </>
      ) : (
        <div className={styles['video-uploader-no-video']}>
          <SvgIcon src={strokeVideoIcon} alt="" width="44" />
          <ModalVideo
            onOpenChange={setIsOpen}
            open={isOpen}
            trigger={
              <Button
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                icon={fullMoreIcon}
                label="Ajouter une URL Youtube"
              />
            }
          />
          <p className={styles['video-uploader-text-subtle']}>
            Affichage de la prévisualisation ici
          </p>
        </div>
      )}
    </div>
  )
}
