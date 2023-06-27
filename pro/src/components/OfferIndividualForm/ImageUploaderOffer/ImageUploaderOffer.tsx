import React from 'react'

import FormLayout from 'components/FormLayout'
import { ImageUploader } from 'components/ImageUploader'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { OfferIndividualImage } from 'core/Offers/types'
import { InfoBox } from 'ui-kit'

import { buildInitialValues } from './utils'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: OfferIndividualImage
}

const ImageUploaderOffer = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
}: ImageUploaderOfferProps) => (
  <FormLayout.Section title="Image de l’offre">
    <FormLayout.Row
      sideComponent={
        <InfoBox>
          Les offres avec une image ont 4 fois plus de chance d’être consultées
          que celles qui n’en ont pas.
        </InfoBox>
      }
    >
      <ImageUploader
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        initialValues={buildInitialValues(imageOffer)}
        mode={UploaderModeEnum.OFFER}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default ImageUploaderOffer
