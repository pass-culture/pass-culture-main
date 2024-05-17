import React from 'react'

import useAnalytics from 'app/App/analytics/firebase'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOfferImage } from 'core/Offers/types'
import { useOfferWizardMode } from 'hooks'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from './ImageUploaderOffer.module.scss'
import { buildInitialValues } from './utils/buildInitialValues'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IndividualOfferImage
}

export const ImageUploaderOffer = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
}: ImageUploaderOfferProps) => {
  const { offer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

  const { logEvent } = useAnalytics()

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      offerId: offer?.id,
      imageType: UploaderModeEnum.OFFER,
      isEdition: mode === OFFER_WIZARD_MODE.EDITION,
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
          className={styles['image-uploader']}
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
