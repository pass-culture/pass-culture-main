import React from 'react'

import FormLayout from 'components/FormLayout'
import { ImageUploader } from 'components/ImageUploader'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { IOfferIndividualImage } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
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
}: IImageUploaderOfferProps) => {
  const { offer } = useOfferIndividualContext()

  const { logEvent } = useAnalytics()

  const logButtonAddClick = () => {
    logEvent?.(Events.CLICKED_ADD_IMAGE, {
      offerId: offer?.id,
      imageType: UploaderModeEnum.OFFER,
    })
  }

  return (
    <FormLayout.Section title="Image de l’offre">
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            Les offres avec une image ont 4 fois plus de chance d’être
            consultées que celles qui n’en ont pas.
          </InfoBox>
        }
      >
        <ImageUploader
          onImageUpload={onImageUpload}
          onImageDelete={onImageDelete}
          initialValues={buildInitialValues(imageOffer)}
          mode={UploaderModeEnum.OFFER}
          onClickButtonImageAdd={logButtonAddClick}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default ImageUploaderOffer
