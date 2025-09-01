import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { Tag } from '@/design-system/Tag/Tag'
import fullEditIcon from '@/icons/full-edit.svg'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeVideoIcon from '@/icons/stroke-video.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { ModalVideo } from './components/ModalVideo/ModalVideo'
import styles from './VideoUploader.module.scss'

export interface VideoUploaderProps {
  videoImageUrl?: string
  videoTitle?: string
  videoDuration?: number
}

export const VideoUploader = ({
  videoImageUrl,
  videoTitle,
  videoDuration,
}: VideoUploaderProps) => {
  return (
    <div className={styles['video-uploader-container']}>
      {videoImageUrl ? (
        <>
          <div className={styles['video-uploader-with-video']}>
            <SafeImage
              alt={'Prévisualisation de l’image'}
              className={styles['video-preview']}
              src={videoImageUrl}
              placeholder={<ImagePlaceholder />}
            />
            <span className={styles['video-duration']}>
              <Tag label={`${videoDuration} min`} />
            </span>
            <p className={styles['video-title']}>{videoTitle}</p>
          </div>

          <div className={styles['action-wrapper']}>
            <ModalVideo
              trigger={
                <Button variant={ButtonVariant.TERNARY} icon={fullEditIcon}>
                  Modifier
                </Button>
              }
            />
            <Button variant={ButtonVariant.TERNARY} icon={fullTrashIcon}>
              Supprimer
            </Button>
          </div>
        </>
      ) : (
        <div className={styles['video-uploader-no-video']}>
          <SvgIcon src={strokeVideoIcon} alt="" width="44" />
          <ModalVideo
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
