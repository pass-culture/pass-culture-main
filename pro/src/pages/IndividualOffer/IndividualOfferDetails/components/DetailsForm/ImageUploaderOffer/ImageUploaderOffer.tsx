import { IndividualOfferImage } from 'commons/core/Offers/types'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from 'components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

import { buildInitialValues } from './buildInitialValues'
import styles from './ImageUploaderOffer.module.scss'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  onImageDropOrSelected?: () => void
  imageOffer?: IndividualOfferImage
  hideActionButtons?: boolean
}

export const ImageUploaderOffer = ({
  onImageUpload,
  onImageDelete,
  onImageDropOrSelected,
  imageOffer,
  hideActionButtons,
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
        initialValues={buildInitialValues(imageOffer)}
        mode={UploaderModeEnum.OFFER}
        onImageDropOrSelected={onImageDropOrSelected}
        hideActionButtons={hideActionButtons}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)
