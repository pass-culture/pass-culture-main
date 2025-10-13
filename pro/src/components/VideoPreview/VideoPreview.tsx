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
}

export const VideoPreview = ({
  videoDuration,
  videoTitle,
  videoThumbnailUrl,
}: VideoPreviewProps) => (
  <div className={styles['video-preview']}>
    <SafeImage
      alt={'Prévisualisation de l’image'}
      className={styles['video-image']}
      src={videoThumbnailUrl}
      placeholder={<ImagePlaceholder />}
    />
    <span className={styles['video-duration']}>
      <Tag label={`${getDurationInMinutes(videoDuration ?? 0)} min`} />
    </span>
    <p className={styles['video-title']}>{videoTitle}</p>
  </div>
)
