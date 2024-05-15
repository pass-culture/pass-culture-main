import { useState } from 'react'
import { useLoaderData } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from 'components/ImageUploader/ButtonImageEdit/types'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { GET_OFFERER_QUERY_KEY } from 'config/swrQueryKeys'
import { Events } from 'core/FirebaseEvents/constants'
import useNotification from 'hooks/useNotification'
import { buildInitialValues } from 'pages/VenueEdition/VenueEditionHeader'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Card } from '../Card'
import { HomepageLoaderData } from '../Homepage'
import { VenueOfferSteps } from '../VenueOfferSteps/VenueOfferSteps'

import styles from './PartnerPage.module.scss'
import { PartnerPageCollectiveSection } from './PartnerPageCollectiveSection'
import { PartnerPageIndividualSection } from './PartnerPageIndividualSection'

export interface PartnerPageProps {
  offerer: GetOffererResponseModel
  venue: GetOffererVenueResponseModel
}

export const PartnerPage = ({ offerer, venue }: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const { venueTypes } = useLoaderData() as HomepageLoaderData
  const venueType = venueTypes.find(
    (venueType) => venueType.id === venue.venueTypeCode
  )
  const initialValues = buildInitialValues(venue.bannerUrl, venue.bannerMeta)
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
      venueId: venue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
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

        <div>
          <div className={styles['venue-type']}>{venueType?.label}</div>
          <div className={styles['venue-name']}>
            {venue.publicName || venue.name}
          </div>

          {venue.street && (
            <address className={styles['venue-address']}>
              {venue.street}, {venue.postalCode} {venue.city}
            </address>
          )}

          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            className={styles['venue-button']}
            link={{
              to: `/structures/${offerer.id}/lieux/${venue.id}`,
              'aria-label': `Gérer la page ${venue.name}`,
            }}
          >
            Gérer ma page
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

      <PartnerPageIndividualSection
        venueId={venue.id}
        isVisibleInApp={Boolean(venue.isVisibleInApp)}
        isDisplayedInHomepage
      />
      <PartnerPageCollectiveSection
        collectiveDmsApplications={venue.collectiveDmsApplications}
        venueId={venue.id}
        allowedOnAdage={offerer.allowedOnAdage}
        isDisplayedInHomepage
      />
    </Card>
  )
}
