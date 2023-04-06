import React from 'react'

import { api } from 'apiClient/api'
import { ImageUploader } from 'components/ImageUploader'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import styles from './ImageVenueUploaderSection.module.scss'

type ImageVenueUploaderSectionProps = {
  venueId: number
  venueImage: string | null
  venueBanner?: IVenueBannerMetaProps | null
  onImageUpload: ({
    bannerUrl,
    bannerMeta,
  }: {
    bannerUrl: string
    bannerMeta: IVenueBannerMetaProps
  }) => void
  onDeleteImage: () => void
}

export interface IVenueBannerMetaProps {
  image_credit: string
  original_image_url: string
  crop_params: IVenueBannerMetaCropParamsProps
}

export interface IVenueBannerMetaCropParamsProps {
  x_crop_percent: number
  y_crop_percent: number
  height_crop_percent: number
  width_crop_percent: number
}

export const ImageVenueUploaderSection = ({
  venueId,
  venueImage,
  venueBanner,
  onImageUpload,
  onDeleteImage,
}: ImageVenueUploaderSectionProps): JSX.Element => {
  let cropParams
  /* istanbul ignore next: DEBT, TO FIX */
  if (venueBanner !== undefined && venueBanner !== null) {
    cropParams = {
      xCropPercent: venueBanner.crop_params.x_crop_percent,
      yCropPercent: venueBanner.crop_params.y_crop_percent,
      heightCropPercent: venueBanner.crop_params.height_crop_percent,
      widthCropPercent: venueBanner.crop_params.width_crop_percent,
    }
  }

  const initialValues = {
    imageUrl: venueImage || undefined,
    originalImageUrl: venueBanner?.original_image_url || undefined,
    cropParams,
    credit: venueBanner?.image_credit,
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: IOnImageUploadArgs) => {
    try {
      const { bannerUrl, bannerMeta } = await postImageToVenue(
        venueId,
        imageFile,
        credit,
        cropParams?.x,
        cropParams?.y,
        cropParams?.height,
        cropParams?.width
      )
      onImageUpload({ bannerUrl, bannerMeta })
      return Promise.resolve()
    } catch {
      return Promise.reject()
    }
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const handleOnImageDelete = async () => {
    try {
      await api.deleteVenueBanner(venueId)
      onDeleteImage()
      return Promise.resolve()
    } catch {
      return Promise.reject()
    }
  }

  return (
    <section
      className={
        'section vp-content-section ' + styles['image-venue-uploader-section']
      }
      data-testid="image-venue-uploader-section"
    >
      <header className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">Image du lieu</h2>
      </header>
      <p className={styles['image-venue-uploader-section-subtitle']}>
        Vous pouvez ajouter une image qui sera visible sur l'application pass
        Culture.
        <br />
        Elle permettra au public de mieux identifier votre lieu.
      </p>
      <ImageUploader
        onImageUpload={handleOnImageUpload}
        onImageDelete={handleOnImageDelete}
        initialValues={initialValues}
        mode={UploaderModeEnum.VENUE}
      />
    </section>
  )
}
