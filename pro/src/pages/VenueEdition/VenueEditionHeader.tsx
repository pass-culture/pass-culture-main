import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  BannerMetaModel,
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { WEBAPP_URL } from 'commons/utils/config'
import { getVenuePagePathToNavigateTo } from 'commons/utils/getVenuePagePathToNavigateTo'
import {
  UploadImageValues,
  UploaderModeEnum,
} from 'commons/utils/imageUploadTypes'
import { ImageDragAndDropUploader } from 'components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { ButtonImageEdit } from 'components/ImageUploader/components/ButtonImageEdit/ButtonImageEdit'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import fullLinkIcon from 'icons/full-link.svg'
import fullParametersIcon from 'icons/full-parameters.svg'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './VenueEditionHeader.module.scss'

export interface VenueEditionHeaderProps {
  venue: GetVenueResponseModel
  offerer: GetOffererResponseModel
  venueTypes: VenueTypeResponseModel[]
  context: 'collective' | 'partnerPage' | 'address'
}

export const buildInitialValues = (
  bannerUrl?: string | null,
  bannerMeta?: BannerMetaModel | null
): UploadImageValues => {
  let cropParams
  if (bannerMeta !== undefined) {
    cropParams = {
      xCropPercent: bannerMeta?.crop_params?.x_crop_percent || 0,
      yCropPercent: bannerMeta?.crop_params?.y_crop_percent || 0,
      heightCropPercent: bannerMeta?.crop_params?.height_crop_percent || 0,
      widthCropPercent: bannerMeta?.crop_params?.width_crop_percent || 0,
    }
  }

  return {
    croppedImageUrl: bannerUrl || undefined,
    originalImageUrl: bannerMeta?.original_image_url || undefined,
    cropParams,
    credit: bannerMeta?.image_credit || '',
  }
}

export const VenueEditionHeader = ({
  venue,
  offerer,
  venueTypes,
  context,
}: VenueEditionHeaderProps) => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const selectedOffererId = useSelector(selectCurrentOffererId)

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
      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])
      notify.success('Vos modifications ont bien été prises en compte')
    } catch {
      notify.error(
        'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
      )
    }
  }

  const handleOnImageDelete = async () => {
    await api.deleteVenueBanner(venue.id)

    setImageValues(buildInitialValues(null, null))
    await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])
    notify.success('Votre image a bien été supprimée')
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
        dragAndDropClassName={styles['image-uploader-drag-and-drop']}
        onImageUpload={handleOnImageUpload}
        onImageDelete={() => {}}
        initialValues={imageValues}
        mode={UploaderModeEnum.VENUE}
        hideActionButtons
        onImageDropOrSelected={logButtonAddClick}
      />

      <div className={styles['venue-details']}>
        <div className={styles['venue-details-main']}>
          <div className={styles['venue-type']}>{venueType?.label}</div>
          <h2 className={styles['venue-name']}>
            {venue.isVirtual
              ? `${offerer.name} (Offre numérique)`
              : venue.publicName || venue.name}
          </h2>
        </div>

        <div className={styles['venue-details-links']}>
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            icon={fullParametersIcon}
            to={getVenuePagePathToNavigateTo(
              venue.managingOfferer.id,
              venue.id,
              '/parametres'
            )}
          >
            Paramètres généraux
          </ButtonLink>
          {venue.isPermanent && context === 'partnerPage' && (
            <ButtonLink
              variant={ButtonVariant.TERNARY}
              icon={fullLinkIcon}
              to={`${WEBAPP_URL}/lieu/${venue.id}`}
              isExternal
              opensInNewTab
            >
              Visualiser votre page
            </ButtonLink>
          )}
          {imageValues.croppedImageUrl && (
            <ButtonImageEdit
              mode={UploaderModeEnum.VENUE}
              initialValues={imageValues}
              onImageUpload={handleOnImageUpload}
              onImageDelete={handleOnImageDelete}
              onClickButtonImage={logButtonAddClick}
            >
              Modifier l’image
            </ButtonImageEdit>
          )}
        </div>
      </div>
    </div>
  )
}
