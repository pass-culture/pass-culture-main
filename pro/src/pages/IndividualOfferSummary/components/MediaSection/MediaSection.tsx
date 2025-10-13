import type { VideoData } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import { VideoPreview } from '@/components/VideoPreview/VideoPreview'

import styles from './MediaSection.module.scss'

export interface MediaSectionProps {
  offerId: number
  imageUrl?: string | null
  videoData?: VideoData
  isOnCreation?: boolean
}

export const MediaSection = ({
  offerId,
  imageUrl,
  videoData,
  isOnCreation = false,
}: MediaSectionProps) => {
  const { videoDuration, videoTitle, videoThumbnailUrl, videoUrl } =
    videoData ?? {}

  return (
    <SummarySection
      title="Image et vidéo"
      editLink={getIndividualOfferUrl({
        offerId,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
        mode: isOnCreation
          ? OFFER_WIZARD_MODE.CREATION
          : OFFER_WIZARD_MODE.EDITION,
      })}
      aria-label="Modifier l’image et la vidéo de l’offre"
      shouldShowDivider
    >
      {!isOnCreation && (
        <SummarySubSection title="Ajoutez une image" shouldShowDivider={false}>
          {imageUrl ? (
            <SafeImage
              className={styles['image-preview']}
              testId="image-preview"
              alt="Prévisualisation de l’image"
              src={imageUrl}
              placeholder={<ImagePlaceholder />}
            />
          ) : (
            <span>{'Pas d’image'}</span>
          )}
        </SummarySubSection>
      )}
      <SummarySubSection title="Ajoutez une vidéo" shouldShowDivider={false}>
        {videoThumbnailUrl ? (
          <VideoPreview
            videoDuration={videoDuration}
            videoTitle={videoTitle}
            videoThumbnailUrl={videoThumbnailUrl}
          />
        ) : (
          <SummaryDescriptionList
            descriptions={[
              {
                title: 'Lien URL de votre vidéo',
                text: videoUrl || ' - ',
              },
            ]}
          />
        )}
      </SummarySubSection>
    </SummarySection>
  )
}
