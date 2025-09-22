import { useState } from 'react'

import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { Tag } from '@/design-system/Tag/Tag'
import fullEditIcon from '@/icons/full-edit.svg'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeVideoIcon from '@/icons/stroke-video.svg'
import { useVideoUploaderContext } from '@/pages/IndividualOffer/IndividualOfferMedia/commons/context/VideoUploaderContext/VideoUploaderContext'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { ModalVideo } from './components/ModalVideo/ModalVideo'
import styles from './VideoUploader.module.scss'

function getDurationInMinutes(videoDuration: number) {
  return Math.round(videoDuration / 60).toLocaleString('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  })
}

export const VideoUploader = () => {
  const [isOpen, setIsOpen] = useState(false)
  const { videoData, onVideoDelete } = useVideoUploaderContext()
  const { videoDuration, videoTitle, videoThumbnailUrl } = videoData ?? {}

  return (
    <div className={styles['video-uploader-container']}>
      {videoThumbnailUrl ? (
        <>
          <div className={styles['video-uploader-with-video']}>
            <SafeImage
              alt={'Prévisualisation de l’image'}
              className={styles['video-preview']}
              src={videoThumbnailUrl}
              placeholder={<ImagePlaceholder />}
            />
            <span className={styles['video-duration']}>
              <Tag label={`${getDurationInMinutes(videoDuration ?? 0)} min`} />
            </span>
            <p className={styles['video-title']}>{videoTitle}</p>
          </div>

          <div className={styles['action-wrapper']}>
            <ModalVideo
              onOpenChange={setIsOpen}
              open={isOpen}
              trigger={
                <Button variant={ButtonVariant.TERNARY} icon={fullEditIcon}>
                  Modifier
                </Button>
              }
            />
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullTrashIcon}
              onClick={onVideoDelete}
            >
              Supprimer
            </Button>
          </div>
        </>
      ) : (
        <div className={styles['video-uploader-no-video']}>
          <SvgIcon src={strokeVideoIcon} alt="" width="44" />
          <ModalVideo
            onOpenChange={setIsOpen}
            open={isOpen}
            trigger={
              <Button variant={ButtonVariant.TERNARY} icon={fullMoreIcon}>
                Ajouter une URL Youtube
              </Button>
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
