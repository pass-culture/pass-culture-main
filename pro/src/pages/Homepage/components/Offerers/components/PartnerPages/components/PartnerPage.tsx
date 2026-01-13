import { useState } from 'react'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { useSWRConfig } from 'swr'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFERER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import {
  UploaderModeEnum,
  type UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Card } from '@/components/Card/Card'
import { ImageUploader } from '@/components/ImageUploader/ImageUploader'
import type { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import fullParametersIcon from '@/icons/full-parameters.svg'
import { VenueOfferSteps } from '@/pages/Homepage/components/VenueOfferSteps/VenueOfferSteps'
import { buildInitialValues } from '@/pages/VenueEdition/components/VenueEditionHeader'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './PartnerPage.module.scss'
import { PartnerPageCollectiveSection } from './PartnerPageCollectiveSection'
import { PartnerPageIndividualSection } from './PartnerPageIndividualSection'

export interface PartnerPageProps {
  offerer: GetOffererResponseModel
  venue: GetVenueResponseModel
  venueHasPartnerPage: boolean
}

export const PartnerPage = ({
  offerer,
  venue,
  venueHasPartnerPage,
}: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const initialValues = buildInitialValues(venue.bannerUrl, venue.bannerMeta)
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const [imageValues, setImageValues] =
    useState<UploadImageValues>(initialValues)

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    const editedVenue = await postImageToVenue(
      venue.id,
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

    await mutate([GET_OFFERER_QUERY_KEY, String(offerer.id)])
  }

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      offererId: selectedOffererId?.toString(),
      venueId: venue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  }

  return (
    <Card>
      <div className={styles['header']}>
        <ImageUploader
          className={styles['image-uploader']}
          onImageUpload={handleOnImageUpload}
          onImageDelete={() => noop}
          initialValues={imageValues}
          hideActionButtons
          onClickButtonImageAdd={logButtonAddClick}
        />

        <div className={styles['venue']}>
          <div className={styles['venue-type']}>{venue.venueType.label}</div>
          <h3 className={styles['venue-name']}>{venue.publicName}</h3>

          {venue.location && (
            <address
              data-testid="venue-address"
              className={styles['venue-address']}
            >
              {withVenueHelpers(venue).fullAddressAsString}
            </address>
          )}
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            icon={fullParametersIcon}
            to={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/parametres`}
          >
            Paramètres généraux
          </ButtonLink>
        </div>
      </div>

      <VenueOfferSteps
        className={styles['venue-offer-steps']}
        offerer={offerer}
        venue={venue}
        hasVenue
        isInsidePartnerBlock
      />
      {venueHasPartnerPage && (
        <PartnerPageIndividualSection
          venueId={venue.id}
          venueName={venue.name}
          offererId={offerer.id}
        />
      )}
      <PartnerPageCollectiveSection
        collectiveDmsApplications={venue.collectiveDmsApplications}
        venueId={venue.id}
        venueName={venue.name}
        offererId={offerer.id}
        allowedOnAdage={offerer.allowedOnAdage}
        isDisplayedInHomepage
      />
    </Card>
  )
}
