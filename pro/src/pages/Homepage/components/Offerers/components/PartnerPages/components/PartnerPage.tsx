import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
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

import { shouldDisplayEACInformationSectionForVenue } from '../../VenueList/venueUtils'
import styles from './PartnerPage.module.scss'
import { PartnerPageCollectiveSection } from './PartnerPageCollectiveSection'
import { PartnerPageIndividualSection } from './PartnerPageIndividualSection'

export const PartnerPage = () => {
  const { logEvent } = useAnalytics()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const { imageValues, handleOnImageUpload } = useOnVenueImageUpload(
    selectedPartnerVenue.id,
    selectedPartnerVenue.bannerUrl,
    selectedPartnerVenue.bannerMeta
  )

  const shouldDisplayVenueOfferSteps =
    shouldDisplayEACInformationSectionForVenue(selectedPartnerVenue)

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      venueId: selectedPartnerVenue.id,
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
          <div className={styles['venue-type']}>
            {selectedPartnerVenue.activity &&
              getActivityLabel(selectedPartnerVenue.activity)}
          </div>
          <h3 className={styles['venue-name']}>
            {selectedPartnerVenue.publicName}
          </h3>

          <address data-testid="venue-address">
            {withVenueHelpers(selectedPartnerVenue).fullAddressAsString}
          </address>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            icon={fullParametersIcon}
            to={`/partenaire/page-individuelle/parametres`}
            label="Paramètres généraux"
          />
        </div>
      </div>

      {shouldDisplayVenueOfferSteps && <VenueOfferSteps />}
      {selectedPartnerVenue.hasPartnerPage && (
        <PartnerPageIndividualSection
          venueId={selectedPartnerVenue.id}
          venueName={selectedPartnerVenue.name}
        />
      )}
      <PartnerPageCollectiveSection isDisplayedInHomepage />
    </Panel>
  )
}
