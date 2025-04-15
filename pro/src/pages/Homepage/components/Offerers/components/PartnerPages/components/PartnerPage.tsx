import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import {
  GetOffererResponseModel,
  VenueTypeResponseModel,
  type GetVenueResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFERER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { Card } from 'components/Card/Card'
import { UploadImageValues } from 'components/ImageUploader/components/ButtonImageEdit/types'
import { OnImageUploadArgs } from 'components/ImageUploader/components/ModalImageEdit/ModalImageEdit'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { VenueOfferSteps } from 'pages/Homepage/components/VenueOfferSteps/VenueOfferSteps'
import { buildInitialValues } from 'pages/VenueEdition/VenueEditionHeader'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import styles from './PartnerPage.module.scss'
import { PartnerPageCollectiveSection } from './PartnerPageCollectiveSection'
import { PartnerPageIndividualSection } from './PartnerPageIndividualSection'

export interface PartnerPageProps {
  offerer: GetOffererResponseModel
  venue: GetVenueResponseModel
  venueTypes: VenueTypeResponseModel[]
  venueHasPartnerPage: boolean
}

export const PartnerPage = ({
  offerer,
  venue,
  venueTypes,
  venueHasPartnerPage,
}: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const venueType = venueTypes.find(
    (venueType) => venueType.id === venue.venueTypeCode
  )
  const initialValues = buildInitialValues(venue.bannerUrl, venue.bannerMeta)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [imageValues, setImageValues] =
    useState<UploadImageValues>(initialValues)

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    try {
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

      notify.success('Vos modifications ont bien été prises en compte')
    } catch {
      notify.error(
        'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
      )
    }
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
          onImageDelete={() => {}}
          initialValues={imageValues}
          mode={UploaderModeEnum.VENUE}
          hideActionButtons
          onClickButtonImageAdd={logButtonAddClick}
        />

        <div className={styles['venue']}>
          <div className={styles['venue-type']}>{venueType?.label}</div>
          <h3 className={styles['venue-name']}>
            {venue.publicName || venue.name}
          </h3>

          {venue.address && (
            <address
              data-testid="venue-address"
              className={styles['venue-address']}
            >
              {venue.address.street ? `${venue.address.street}, ` : ''}
              {venue.address.postalCode} {venue.address.city}
            </address>
          )}
        </div>
      </div>

      <VenueOfferSteps
        className={styles['venue-offer-steps']}
        offerer={offerer}
        venue={{
          ...venue,
          hasCreatedOffer: venue.hasOffers,
        }}
        hasVenue
        isInsidePartnerBlock
      />
      {venueHasPartnerPage && (
        <PartnerPageIndividualSection
          venueId={venue.id}
          venueName={venue.name}
          offererId={offerer.id}
          isVisibleInApp={Boolean(venue.isVisibleInApp)}
          isDisplayedInHomepage
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
