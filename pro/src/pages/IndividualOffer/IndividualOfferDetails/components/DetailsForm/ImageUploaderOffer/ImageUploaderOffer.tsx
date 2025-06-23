import { IndividualOfferImage } from 'commons/core/Offers/types'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from 'components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

import { buildInitialValues } from './buildInitialValues'
import styles from './ImageUploaderOffer.module.scss'

export interface ImageUploaderOfferProps {
  displayedImage?: IndividualOfferImage | OnImageUploadArgs
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  onImageDropOrSelected?: () => void
  hideActionButtons?: boolean
  isDisabled?: boolean
}

export const ImageUploaderOffer = ({
  displayedImage,
  onImageUpload,
  onImageDelete,
  onImageDropOrSelected,
  hideActionButtons,
  isDisabled = false,
}: ImageUploaderOfferProps) => (
  <FormLayout.Section title="Illustrez votre offre">
    <FormLayout.Row>
      <p>
        Ajoutez une image pour que votre offre ait 2 fois plus de chances d’être
        consultée !
      </p>
      <ImageDragAndDropUploader
        className={styles['image-uploader']}
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        initialValues={buildInitialValues(displayedImage)}
        mode={UploaderModeEnum.OFFER}
        onImageDropOrSelected={onImageDropOrSelected}
        hideActionButtons={hideActionButtons}
        disabled={isDisabled}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)
