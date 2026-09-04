import { useId } from 'react'

import type { VideoData } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { isSelectedPartnerOrOffererClosed } from '@/commons/utils/isSelectedPartnerOrOffererClosed'
import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { VideoPreview } from '@/components/VideoPreview/VideoPreview'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import styles from './MediaSection.module.scss'

export interface MediaSectionProps {
  offerId: number
  imageUrl?: string | null
  imageCredit?: string | null
  videoData?: VideoData
  isOnCreation?: boolean
}

export const MediaSection = ({
  offerId,
  imageUrl,
  imageCredit,
  videoData,
  isOnCreation = false,
}: MediaSectionProps) => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isClosed = isSelectedPartnerOrOffererClosed(selectedPartnerVenue)
  const imageCreditId = useId()

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
      isReadOnly={isClosed}
      shouldShowDivider
    >
      {!isOnCreation && (
        <SummarySubSection title="Ajoutez une image" shouldShowDivider={false}>
          {imageUrl ? (
            <figure>
              <SafeImage
                className={styles['image-preview']}
                testId="image-preview"
                alt="Prévisualisation de l’image"
                src={imageUrl}
                placeholder={<ImagePlaceholder />}
                ariaDescribedBy={imageCredit ? imageCreditId : undefined}
              />
              {imageCredit ? (
                <figcaption id={imageCreditId}>
                  <p className={styles['image-credit-text']}>
                    Crédit image : {imageCredit}
                  </p>
                </figcaption>
              ) : null}
            </figure>
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
