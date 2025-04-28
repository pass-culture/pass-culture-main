import { useSelector } from 'react-redux'

import { useAnalytics } from 'app/App/analytics/firebase'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from 'components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

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
      imageCreationStage: 'add image',
    })
  }

  return (
    <FormLayout.Section title="Illustrez votre offre">
      <FormLayout.Row>
        <p>
          Ajoutez une image pour que votre offre ait 2 fois plus de chances
          d’être consultée !
        </p>
        <ImageDragAndDropUploader
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
