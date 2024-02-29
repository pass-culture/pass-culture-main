import { useFormikContext } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import { BannerMetaModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { ImageUploader } from 'components/ImageUploader'
import { UploadImageValues } from 'components/ImageUploader/ButtonImageEdit'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import { VenueFormValues } from '../types'

/* istanbul ignore next: DEBT, TO FIX */
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

interface ImageUploaderProps {
  isCreatingVenue: boolean
}

/* istanbul ignore next: DEBT, TO FIX */
const ImageUploaderVenue = ({ isCreatingVenue }: ImageUploaderProps) => {
  const notify = useNotification()
  const {
    setFieldValue,
    values: { id: venueId, bannerUrl, bannerMeta },
  } = useFormikContext<VenueFormValues>()
  const { logEvent } = useAnalytics()

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    try {
      const editedVenue = await postImageToVenue(
        venueId || 0,
        imageFile,
        credit,
        cropParams?.x,
        cropParams?.y,
        cropParams?.height,
        cropParams?.width
      )

      await setFieldValue('bannerUrl', editedVenue.bannerUrl)
      await setFieldValue('bannerMeta', editedVenue.bannerMeta)
      logEvent?.(VenueEvents.UPLOAD_IMAGE, {
        from: location.pathname,
        venueId: venueId,
      })
      notify.success('Vos modifications ont bien été prises en compte')
      return Promise.resolve()
    } catch {
      notify.error(
        'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
      )
      return Promise.reject()
    }
  }

  const handleOnImageDelete = async () => {
    try {
      await api.deleteVenueBanner(venueId || 0)

      await setFieldValue('bannerUrl', undefined)
      await setFieldValue('bannerMeta', undefined)

      return Promise.resolve()
    } catch {
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
      return Promise.reject()
    }
  }

  const logButtonAddClick = () => {
    logEvent?.(Events.CLICKED_ADD_IMAGE, {
      venueId: venueId,
      imageType: UploaderModeEnum.VENUE,
      isEdition: !isCreatingVenue,
    })
  }

  return (
    <FormLayout.Section
      title="Ajouter une image"
      description={`Vous pouvez ajouter une image qui sera visible sur l’application pass Culture.
      Elle permettra au public de mieux identifier votre lieu.`}
    >
      <FormLayout.Row>
        <ImageUploader
          onImageUpload={handleOnImageUpload}
          onImageDelete={handleOnImageDelete}
          initialValues={buildInitialValues(bannerUrl, bannerMeta || undefined)}
          mode={UploaderModeEnum.VENUE}
          onClickButtonImageAdd={logButtonAddClick}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ImageUploaderVenue
