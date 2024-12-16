import React from 'react'
import { useSelector } from 'react-redux'

import { useAnalytics } from 'app/App/analytics/firebase'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { buildInitialValues } from './buildInitialValues'
import styles from './ImageUploaderOffer.module.scss'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IndividualOfferImage
  hideActionButtons?: boolean
}

export const ImageUploaderOffer = ({
  onImageUpload,
  onImageDelete,
  imageOffer,
  hideActionButtons,
}: ImageUploaderOfferProps) => {
  const { offer } = useIndividualOfferContext()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const mode = useOfferWizardMode()

  const { logEvent } = useAnalytics()

  const logButtonAddClick = () => {
    logEvent(Events.CLICKED_ADD_IMAGE, {
      offererId: selectedOffererId?.toString(),
      offerId: offer?.id,
      offerType: 'individual',
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
          hideActionButtons={hideActionButtons}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
