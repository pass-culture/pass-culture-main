import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { ImageUploader } from '@/components/ImageUploader/ImageUploader'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullParametersIcon from '@/icons/full-parameters.svg'
import { VenueOfferSteps } from '@/pages/Homepage/components/VenueOfferSteps/VenueOfferSteps'
import { Panel } from '@/ui-kit/Panel/Panel'

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
  const selectedOffererId = useAppSelector(selectCurrentOffererId)

  const { imageValues, handleOnImageUpload } = useOnVenueImageUpload(
    venue.id,
    venue.bannerUrl,
    venue.bannerMeta
  )

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
    <Panel>
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
            <address data-testid="venue-address">
              {withVenueHelpers(venue).fullAddressAsString}
            </address>
          )}
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            icon={fullParametersIcon}
            to={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/parametres`}
            label="Paramètres généraux"
          />
        </div>
      </div>

      <VenueOfferSteps offerer={offerer} venue={venue} hasVenue />
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
        allowedOnAdage={venue.allowedOnAdage}
        isDisplayedInHomepage
      />
    </Panel>
  )
}
