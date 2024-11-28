import React from 'react'

import { OfferCollectiveImage } from 'commons/core/Offers/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from 'components/ImageUploader/ButtonImageEdit/types'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  imageOffer: OfferCollectiveImage | null
  disableForm: boolean
}

const buildInitialValues = (
  imageOffer: OfferCollectiveImage | null
): UploadImageValues => ({
  imageUrl: imageOffer?.url || '',
  originalImageUrl: imageOffer?.url || '',
  credit: imageOffer?.credit || '',
})

export const FormImageUploader = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
  disableForm
}: ImageUploaderOfferProps) => (
  <FormLayout.Section title="Image de l’offre">
    <FormLayout.Row>
      <ImageUploader
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        initialValues={buildInitialValues(imageOffer)}
        mode={UploaderModeEnum.OFFER_COLLECTIVE}
        disableForm={disableForm}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)
