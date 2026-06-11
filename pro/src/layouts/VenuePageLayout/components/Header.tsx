import { apiNew } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { buildInitialVenueImageValues } from '@/commons/core/Venue/utils/buildInitialVenueImageValues'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { WEBAPP_URL } from '@/commons/utils/config'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { noop } from '@/commons/utils/noop'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { ButtonImageEdit } from '@/components/ImageUploader/components/ButtonImageEdit/ButtonImageEdit'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'

import styles from './Header.module.scss'

export interface HeaderProps {
  context: 'collective' | 'partnerPage'
}
export const Header = ({ context }: Readonly<HeaderProps>) => {
  const { logEvent } = useAnalytics()
  const { syncVenue } = useSyncVenueCache()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const snackBar = useSnackBar()

  const { imageValues, setImageValues, handleOnImageUpload } =
    useOnVenueImageUpload(
      selectedPartnerVenue.id,
      selectedPartnerVenue.bannerUrl,
      selectedPartnerVenue.bannerMeta
    )

  const handleOnImageDelete = async () => {
    try {
      await apiNew.deleteVenueBanner({
        path: { venue_id: selectedPartnerVenue.id },
      })
      setImageValues(buildInitialVenueImageValues(null, null))
      await syncVenue(selectedPartnerVenue.id)

      snackBar.success('Votre image a bien été supprimée')
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de la suppression de l'image"
      )
    }
  }

  const logButtonAddClick = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
      imageCreationStage: 'add image',
    })
  }

  return (
    <div className={styles['header']}>
      <ImageDragAndDropUploader
        className={styles['image-uploader']}
        // check-unused-css-disable-next-line
        dragAndDropClassName={styles['image-uploader-drag-and-drop']}
        onImageUpload={handleOnImageUpload}
        onImageDelete={noop}
        initialValues={imageValues}
        mode={UploaderModeEnum.VENUE}
        hideActionButtons
        onImageDropOrSelected={logButtonAddClick}
      />

      <div className={styles['venue-details']}>
        <div className={styles['venue-details-main']}>
          <div className={styles['venue-type']}>
            {selectedPartnerVenue.activity &&
              getActivityLabel(selectedPartnerVenue.activity)}
          </div>
          <h2 className={styles['venue-name']}>
            {selectedPartnerVenue.publicName}
          </h2>
        </div>

        <div className={styles['venue-details-links']}>
          {selectedPartnerVenue.isPermanent && context === 'partnerPage' && (
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              to={`${WEBAPP_URL}/lieu/${selectedPartnerVenue.id}`}
              isExternal
              opensInNewTab
              label="Visualiser votre page"
            />
          )}
          {imageValues.croppedImageUrl && (
            <ButtonImageEdit
              mode={UploaderModeEnum.VENUE}
              initialValues={imageValues}
              onImageUpload={handleOnImageUpload}
              onImageDelete={handleOnImageDelete}
              onClickButtonImage={logButtonAddClick}
              label="Modifier l’image"
            />
          )}
        </div>
      </div>
    </div>
  )
}
