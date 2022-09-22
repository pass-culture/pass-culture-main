import React from 'react'

import { IOfferIndividualImage } from 'core/Offers/types'
import FormLayout from 'new_components/FormLayout'
import { ImageUploader } from 'new_components/ImageUploader'
import { IUploadImageValues } from 'new_components/ImageUploader/ButtonImageEdit'
import { IOnImageUploadArgs } from 'new_components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'

interface IImageUploaderOfferProps {
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IOfferIndividualImage
}

const buildInitialValues = (
  imageUrl?: string,
  credit?: string
): IUploadImageValues => {
  return {
    imageUrl,
    originalImageUrl: imageUrl || '',
    credit: credit || '',
    cropParams: {
      xCropPercent: 1,
      yCropPercent: 1,
      heightCropPercent: 0,
      widthCropPercent: 0,
    },
  }
}

const ImageUploaderOffer = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
}: IImageUploaderOfferProps) => {
  const { url: imageUrl, credit } = imageOffer || {}

  return (
    <FormLayout.Section title="Image de l'offre">
      <FormLayout.Row>
        <ImageUploader
          onImageUpload={onImageUpload}
          onImageDelete={onImageDelete}
          initialValues={buildInitialValues(imageUrl, credit)}
          mode={UploaderModeEnum.OFFER}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ImageUploaderOffer
