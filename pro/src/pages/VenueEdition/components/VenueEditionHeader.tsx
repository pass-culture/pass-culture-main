import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnVenueImageUpload } from '@/commons/core/Venue/hooks/useOnVenueImageUpload'
import { buildInitialVenueImageValues } from '@/commons/core/Venue/utils/buildInitialVenueImageValues'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { setSelectedVenue } from '@/commons/store/user/reducer'
import { WEBAPP_URL } from '@/commons/utils/config'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
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
import fullParametersIcon from '@/icons/full-parameters.svg'

import styles from './VenueEditionHeader.module.scss'

export interface VenueEditionHeaderProps {
  venue: GetVenueResponseModel
  context: 'collective' | 'partnerPage' | 'address'
}

export const VenueEditionHeader = ({
  venue,
  context,
}: VenueEditionHeaderProps) => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const dispatch = useAppDispatch()
  const snackBar = useSnackBar()

  const { imageValues, setImageValues, handleOnImageUpload } =
    useOnVenueImageUpload(venue.id, venue.bannerUrl, venue.bannerMeta)

  const handleOnImageDelete = async () => {
    try {
      await api.deleteVenueBanner(venue.id)
      setImageValues(buildInitialVenueImageValues(null, null))

      const updatedVenue = await mutate(
        [GET_VENUE_QUERY_KEY, String(venue.id)],
        () => api.getVenue(venue.id)
      )
      if (updatedVenue) {
        dispatch(setSelectedVenue(updatedVenue))
      }
      snackBar.success('Votre image a bien été supprimée')
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de la suppression de l'image"
      )
    }
  }

  const logButtonAddClick = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      offererId: selectedOffererId?.toString(),
      venueId: venue.id,
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
        onImageDelete={() => noop}
        initialValues={imageValues}
        mode={UploaderModeEnum.VENUE}
        hideActionButtons
        onImageDropOrSelected={logButtonAddClick}
      />

      <div className={styles['venue-details']}>
        <div className={styles['venue-details-main']}>
          <div className={styles['venue-type']}>{venue.venueType.label}</div>
          <h2 className={styles['venue-name']}>
            {venue.isVirtual
              ? `${venue.managingOfferer.name} (Offre numérique)`
              : venue.publicName}
          </h2>
        </div>

        <div className={styles['venue-details-links']}>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            icon={fullParametersIcon}
            to={getVenuePagePathToNavigateTo(
              venue.managingOfferer.id,
              venue.id,
              '/parametres'
            )}
            label="Paramètres généraux"
          />
          {venue.isPermanent && context === 'partnerPage' && (
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              to={`${WEBAPP_URL}/lieu/${venue.id}`}
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
