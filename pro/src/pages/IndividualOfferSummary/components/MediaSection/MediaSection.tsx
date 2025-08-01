import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { ImagePlaceholder } from 'components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from 'components/SafeImage/SafeImage'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import styles from './MediaSection.module.scss'

export interface MediaSectionProps {
  offerId: number
  imageUrl?: string | null
  videoUrl?: string | null
  shouldImageBeHidden?: boolean
}

export const MediaSection = ({
  offerId,
  imageUrl,
  videoUrl,
  shouldImageBeHidden = false,
}: MediaSectionProps) => {
  return (
    <SummarySection
      title="Image et vidéo"
      editLink={getIndividualOfferUrl({
        offerId,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
        mode: OFFER_WIZARD_MODE.EDITION,
      })}
      aria-label="Modifier les détails de l’offre"
    >
      {!shouldImageBeHidden && (
        <SummarySubSection title="Ajoutez une image">
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
      <SummarySubSection title="Ajoutez une vidéo">
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Lien URL de votre vidéo',
              text: videoUrl || ' - ',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}
