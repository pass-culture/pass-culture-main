import { useFormikContext } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import useNotification from 'components/hooks/useNotification'
import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'
import FormLayout from 'new_components/FormLayout'
import { ImageUploader } from 'new_components/ImageUploader'
import { IUploadImageValues } from 'new_components/ImageUploader/ButtonImageEdit'
import { IOnImageUploadArgs } from 'new_components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import { IVenueFormValues } from '../types'

import styles from './ImageUploaderVenue.module.scss'

/* istanbul ignore next: DEBT, TO FIX */
const buildInitialValues = (
  bannerUrl?: string,
  bannerMeta?: IVenueBannerMetaProps
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
      const editedVenue = await postImageToVenue({
        venueId,
        banner: imageFile,
        xCropPercent: cropParams?.x,
        yCropPercent: cropParams?.y,
        heightCropPercent: cropParams?.height,
        widthCropPercent: cropParams?.width,
        imageCredit: credit,
      })

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
      await api.deleteVenueBanner(venueId)

      setFieldValue('bannerUrl', undefined)
      setFieldValue('bannerMeta', undefined)

      return Promise.resolve()
    } catch {
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
      return Promise.reject()
    }
  }

  return (
    <FormLayout.Section title="Image du lieu">
      <p className={styles['explanatory-text']}>
        Vous pouvez ajouter une image qui sera visible sur l’application pass
        Culture.
        <br />
        Elle permettra au public de mieux identifier votre lieu.
      </p>
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
