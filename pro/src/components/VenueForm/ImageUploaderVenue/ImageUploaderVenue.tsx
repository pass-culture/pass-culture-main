import { useFormikContext } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { ImageUploader } from 'components/ImageUploader'
import { IUploadImageValues } from 'components/ImageUploader/ButtonImageEdit'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import useNotification from 'hooks/useNotification'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import { IVenueFormValues } from '../types'

interface VenueBannerMetaCropParamsProps {
  x_crop_percent: number
  y_crop_percent: number
  height_crop_percent: number
  width_crop_percent: number
}

export interface VenueBannerMetaProps {
  image_credit: string
  original_image_url: string
  crop_params: VenueBannerMetaCropParamsProps
}

/* istanbul ignore next: DEBT, TO FIX */
const buildInitialValues = (
  bannerUrl?: string,
  bannerMeta?: VenueBannerMetaProps
): IUploadImageValues => {
  let cropParams
  if (bannerMeta !== undefined) {
    cropParams = {
      xCropPercent: bannerMeta.crop_params.x_crop_percent,
      yCropPercent: bannerMeta.crop_params.y_crop_percent,
      heightCropPercent: bannerMeta.crop_params.height_crop_percent,
      widthCropPercent: bannerMeta.crop_params.width_crop_percent,
    }
  }

  return {
    imageUrl: bannerUrl || undefined,
    originalImageUrl: bannerMeta?.original_image_url || undefined,
    cropParams,
    credit: bannerMeta?.image_credit,
  }
}

/* istanbul ignore next: DEBT, TO FIX */
const ImageUploaderVenue = () => {
  const notify = useNotification()
  const {
    setFieldValue,
    values: { id: venueId, bannerUrl, bannerMeta },
  } = useFormikContext<IVenueFormValues>()

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: IOnImageUploadArgs) => {
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

      setFieldValue('bannerUrl', editedVenue.bannerUrl)
      setFieldValue('bannerMeta', editedVenue.bannerMeta)
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

      setFieldValue('bannerUrl', undefined)
      setFieldValue('bannerMeta', undefined)

      return Promise.resolve()
    } catch {
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
      return Promise.reject()
    }
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
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ImageUploaderVenue
