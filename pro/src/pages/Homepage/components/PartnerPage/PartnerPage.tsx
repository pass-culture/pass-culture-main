import { useState } from 'react'
import { mutate } from 'swr'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { WEBAPP_URL } from '@/commons/utils/config'
import {
  UploaderModeEnum,
  type UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import type { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { buildInitialValues } from '@/pages/VenueEdition/components/VenueEditionHeader'
import { postImageToVenue } from '@/repository/pcapi/pcapi'
import { Panel } from '@/ui-kit/Panel/Panel'

import styles from './PartnerPage.module.scss'

type PartnerPageProps = {
  venue: GetVenueResponseModel
}

export const PartnerPage = ({ venue }: PartnerPageProps) => {
  const { logEvent } = useAnalytics()

  const initialValues = buildInitialValues(venue.bannerUrl, venue.bannerMeta)
  const [imageValues, setImageValues] =
    useState<UploadImageValues>(initialValues)
  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venue.id}`
  const venueId = venue.id
  const offererId = venue.managingOfferer.id

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    const editedVenue = await postImageToVenue(
      venueId,
      imageFile,
      credit,
      cropParams?.x,
      cropParams?.y,
      cropParams?.height,
      cropParams?.width
    )
    setImageValues(
      buildInitialValues(editedVenue.bannerUrl, editedVenue.bannerMeta)
    )

    await mutate([GET_VENUE_QUERY_KEY, String(venueId)])
  }

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      offererId: offererId.toString(),
      venueId: venue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  }

  return (
    <Panel>
      <div className={styles['container']}>
        <h2 className={styles['title']}>Votre page sur l'application</h2>
        <ImageDragAndDropUploader
          onImageUpload={handleOnImageUpload}
          onImageDelete={() => noop}
          mode={UploaderModeEnum.VENUE}
          initialValues={imageValues}
          hideActionButtons
          onImageDropOrSelected={logButtonAddClick}
        />
        <h3 className={styles['title']}>{venue.name}</h3>
        <div className={styles['buttons']}>
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
        </div>
      </div>
    </Panel>
  )
}
