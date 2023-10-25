import React from 'react'

import FormLayout from 'components/FormLayout'
import { ImageUploader, UploadImageValues } from 'components/ImageUploader'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { OfferCollectiveImage } from 'core/Offers/types'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  imageOffer: OfferCollectiveImage | null
}

const buildInitialValues = (
  imageOffer: OfferCollectiveImage | null
): UploadImageValues => ({
  imageUrl: imageOffer?.url || '',
  originalImageUrl: imageOffer?.url || '',
  credit: imageOffer?.credit || '',
})

const FormImageUploader = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
}: ImageUploaderOfferProps) => (
  <FormLayout.Section title="Image de l’offre">
    <FormLayout.Row>
      <ImageUploader
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        initialValues={buildInitialValues(imageOffer)}
        mode={UploaderModeEnum.OFFER_COLLECTIVE}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default FormImageUploader
