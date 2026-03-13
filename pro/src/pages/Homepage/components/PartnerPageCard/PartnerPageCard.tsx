import type { BannerMetaModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { WEBAPP_URL } from '@/commons/utils/config'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import styles from './PartnerPageCard.module.scss'

type PartnerPageProps = {
  venueId: number
  venueName: string
  offererId: number
  venueBannerUrl?: string | null
  venueBannerMeta?: BannerMetaModel | null
}

export const PartnerPageCard = ({
  venueId,
  venueName,
  offererId,
  venueBannerUrl,
  venueBannerMeta,
}: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
  const { imageValues, handleOnImageUpload } = useOnVenueImageUpload(
    venueId,
    venueBannerUrl,
    venueBannerMeta
  )
  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venueId}`

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      offererId: offererId.toString(),
      venueId,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  }

  return (
    <Card>
      <Card.Header title="Votre page sur l'application" titleTag="h2" />
      <Card.Content>
        <ImageDragAndDropUploader
          onImageUpload={handleOnImageUpload}
          onImageDelete={() => noop}
          mode={UploaderModeEnum.VENUE}
          initialValues={imageValues}
          hideActionButtons
          onImageDropOrSelected={logButtonAddClick}
        />
        <h3 className={styles['title']}>{venueName}</h3>
      </Card.Content>
      <Card.Footer>
        <Button
          label="Compléter ma page"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          to={`/structures/${offererId}/lieux/${venueId}/page-partenaire`}
          as="a"
        />
        <Button
          label="Voir ma page"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          isExternal
          to={venuePreviewLink}
          as="a"
          opensInNewTab
        />
      </Card.Footer>
    </Card>
  )
}
