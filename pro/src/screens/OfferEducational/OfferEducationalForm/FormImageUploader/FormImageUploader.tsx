import React from 'react'

import FormLayout from 'components/FormLayout'
import { ImageUploader, IUploadImageValues } from 'components/ImageUploader'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { IOfferCollectiveImage } from 'core/Offers/types'

export interface IImageUploaderOfferProps {
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer: IOfferCollectiveImage | null
}

const buildInitialValues = (
  imageOffer: IOfferCollectiveImage | null
): IUploadImageValues => ({
  imageUrl: imageOffer?.url || '',
  originalImageUrl: imageOffer?.url || '',
  credit: imageOffer?.credit || '',
})

const FormImageUploader = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
}: IImageUploaderOfferProps) => (
  <FormLayout.Section title="Image de l'offre">
    <FormLayout.Row>
      <ImageUploader
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        initialValues={buildInitialValues(imageOffer)}
        mode={UploaderModeEnum.OFFER}
        showPreviewInModal={false}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default FormImageUploader
