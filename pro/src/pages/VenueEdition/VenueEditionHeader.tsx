import { useState } from 'react'

import { api } from 'apiClient/api'
import {
  BannerMetaModel,
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { ButtonImageEdit } from 'components/ImageUploader/ButtonImageEdit/ButtonImageEdit'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from 'components/ImageUploader/ButtonImageEdit/types'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Events } from 'core/FirebaseEvents/constants'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { useNotification } from 'hooks/useNotification'
import fullPlusIcon from 'icons/full-more.svg'
import fullParametersIcon from 'icons/full-parameters.svg'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './VenueEditionHeader.module.scss'

export interface VenueEditionHeaderProps {
  venue: GetVenueResponseModel
  offerer: GetOffererResponseModel
  venueTypes: VenueTypeResponseModel[]
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
    imageUrl: bannerUrl || undefined,
    originalImageUrl: bannerMeta?.original_image_url || undefined,
    cropParams,
    credit: bannerMeta?.image_credit || '',
  }
}

export const VenueEditionHeader = ({
  venue,
  offerer,
  venueTypes,
}: VenueEditionHeaderProps) => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const isNewSideBarNavigation = useIsNewInterfaceActive()

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
    notify.success('Votre image a bien été supprimée')
  }

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      venueId: venue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
    })
  }

  return (
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

      <div className={styles['venue-details']}>
        <div className={styles['venue-type']}>{venueType?.label}</div>
        {isNewSideBarNavigation ? (
          <h2 className={styles['venue-name']}>
            {venue.isVirtual
              ? `${offerer.name} (Offre numérique)`
              : venue.publicName || venue.name}
          </h2>
        ) : (
          <h1 className={styles['venue-name']}>
            {venue.isVirtual
              ? `${offerer.name} (Offre numérique)`
              : venue.publicName || venue.name}
          </h1>
        )}

        {venue.street && (
          <address className={styles['venue-address']}>
            {venue.street}, {venue.postalCode} {venue.city}
          </address>
        )}

        <ButtonLink
          variant={ButtonVariant.TERNARY}
          icon={fullParametersIcon}
          link={{
            to: `/structures/${venue.managingOfferer.id}/lieux/${venue.id}/parametres`,
          }}
        >
          Paramètres généraux
        </ButtonLink>

        {imageValues.originalImageUrl && (
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

        {!isNewSideBarNavigation && (
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            icon={fullPlusIcon}
            className={styles['venue-button']}
            link={{
              to: `/offre/creation?lieu=${venue.id}&structure=${offerer.id}`,
            }}
          >
            Créer une offre
          </ButtonLink>
        )}
      </div>
    </div>
  )
}
