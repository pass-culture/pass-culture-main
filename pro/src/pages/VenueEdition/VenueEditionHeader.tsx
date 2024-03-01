import { useState } from 'react'

import {
  BannerMetaModel,
  GetOffererResponseModel,
  GetVenueResponseModel,
} from 'apiClient/v1'
import { ImageUploader, UploadImageValues } from 'components/ImageUploader'
import { ButtonImageEdit } from 'components/ImageUploader/ButtonImageEdit'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Events } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullPlusIcon from 'icons/full-more.svg'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './VenueEditionHeader.module.scss'

export interface VenueEditionHeaderProps {
  venue: GetVenueResponseModel
  offerer: GetOffererResponseModel
  venueTypes: SelectOption[]
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
  const isNewBankDetailsEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const venueType = venueTypes.find(
    (venueType) => venueType.value === venue.venueTypeCode
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

  const logButtonAddClick = () => {
    logEvent?.(Events.CLICKED_ADD_IMAGE, {
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

      <div>
        <div className={styles['venue-type']}>{venueType?.label}</div>
        <h1 className={styles['venue-name']}>
          {venue.isVirtual
            ? `${offerer.name} (Offre numérique)`
            : venue.publicName || venue.name}
        </h1>

        {venue.address && (
          <address className={styles['venue-address']}>
            {venue.address}, {venue.postalCode} {venue.city}
          </address>
        )}

        {!isNewBankDetailsEnabled && (
          <div style={{ marginBottom: '16px' }}>
            {/* For the screen reader to spell-out the id, we add a
          visually hidden span with a space between each character.
          The other span will be hidden from the screen reader. */}
            <span className="visually-hidden">
              Identifiant du lieu : {venue.dmsToken.split('').join(' ')}
            </span>
            <span aria-hidden={true}>
              Identifiant du lieu : {venue.dmsToken}
            </span>
          </div>
        )}

        <hr className={styles['separator']} />

        {imageValues.imageUrl && (
          <div>
            <ButtonImageEdit
              mode={UploaderModeEnum.VENUE}
              initialValues={imageValues}
              onImageUpload={handleOnImageUpload}
              onClickButtonImage={logButtonAddClick}
            >
              Modifier l’image
            </ButtonImageEdit>
          </div>
        )}

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
      </div>
    </div>
  )
}
