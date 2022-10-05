import React from 'react'

import { IOfferIndividualImage } from 'core/Offers/types'
import FormLayout from 'new_components/FormLayout'
import { ImageUploader } from 'new_components/ImageUploader'
import { IOnImageUploadArgs } from 'new_components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'
import { InfoBox } from 'ui-kit'

import { buildInitialValues } from './utils'

export interface IImageUploaderOfferProps {
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IOfferIndividualImage
}

const ImageUploaderOffer = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
}: IImageUploaderOfferProps) => (
  <FormLayout.Section title="Image de l'offre">
    <FormLayout.Row
      sideComponent={
        <InfoBox
          type="info"
          text="Les offres avec une image ont 4 fois plus de chance d’être consultées que celles qui n’en ont pas."
        />
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
