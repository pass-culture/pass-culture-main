import { useId } from 'react'

import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { Tag } from '@/design-system/Tag/Tag'

import styles from './VideoPreview.module.scss'

function getDurationInMinutes(videoDuration: number) {
  return Math.round(videoDuration / 60).toLocaleString('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  })
}

type VideoPreviewProps = {
  videoDuration?: number | null
  videoTitle?: string | null
  videoThumbnailUrl: string
  videoDescription?: string | null
}

export const VideoPreview = ({
  videoDuration,
  videoTitle,
  videoThumbnailUrl,
  videoDescription,
}: VideoPreviewProps) => {
  const previewId = useId()

  return (
    <figure className={styles['video-figure']}>
      <div className={styles['video-preview']}>
        <SafeImage
          ariaDescribedBy={previewId}
          alt="Prévisualisation de la vidéo"
          className={styles['video-image']}
          src={videoThumbnailUrl}
          placeholder={
            <ImagePlaceholder isVideo alt="Prévisualisation de la vidéo" />
          }
        />
        <span className={styles['video-duration']}>
          <Tag label={`${getDurationInMinutes(videoDuration ?? 0)} min`} />
        </span>
        <p className={styles['video-title']}>{videoTitle}</p>
      </div>
      <figcaption id={previewId} className={styles['video-description']}>
        <p>
          <strong>Description textuelle de la vidéo :</strong>{' '}
          {videoDescription
            ? videoDescription
            : 'Aucune description textuelle renseignée'}
        </p>
      </figcaption>
    </figure>
  )
}
