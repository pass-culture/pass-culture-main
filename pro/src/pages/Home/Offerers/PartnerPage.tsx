import { useState } from 'react'
import { useLoaderData } from 'react-router-dom'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { ImageUploader, UploadImageValues } from 'components/ImageUploader'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { buildInitialValues } from 'components/VenueForm/ImageUploaderVenue/ImageUploaderVenue'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { ButtonLink } from 'ui-kit'
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
  setSelectedOfferer: (offerer: GetOffererResponseModel) => void
}

export const PartnerPage = ({
  offerer,
  venue,
  setSelectedOfferer,
}: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
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
      // we update the offerer state to keep venue with its new image
      setSelectedOfferer({
        ...offerer,
        managedVenues: (offerer.managedVenues ?? []).map((iteratedVenue) =>
          iteratedVenue.id === venue.id
            ? {
                ...venue,
                bannerUrl: editedVenue.bannerUrl,
                bannerMeta: editedVenue.bannerMeta,
              }
            : iteratedVenue
        ),
      })

      notify.success('Vos modifications ont bien été prises en compte')
    } catch {
      notify.error(
        'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
      )
    }
  }

  const logButtonAddClick = () => {
    logEvent?.(Events.CLICKED_ADD_IMAGE, {
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

          {venue.address && (
            <address className={styles['venue-address']}>
              {venue.address}, {venue.postalCode} {venue.city}
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
        displayTitle
      />
      <PartnerPageCollectiveSection
        collectiveDmsApplications={venue.collectiveDmsApplications}
        venueId={venue.id}
        hasAdageId={venue.hasAdageId}
        displayTitle
      />
    </Card>
  )
}
