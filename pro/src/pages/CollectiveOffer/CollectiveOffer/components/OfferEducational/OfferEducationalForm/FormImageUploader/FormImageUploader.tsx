import { OfferCollectiveImage } from '@/commons/core/Offers/types'
import {
  UploaderModeEnum,
  UploadImageValues,
} from '@/commons/utils/imageUploadTypes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  onImageDropOrSelected?: () => void
  imageOffer: OfferCollectiveImage | null
  disableForm: boolean
  isTemplate: boolean
}

const buildInitialValues = (
  imageOffer: OfferCollectiveImage | null
): UploadImageValues => ({
  croppedImageUrl: imageOffer?.url || '',
  credit: imageOffer?.credit || '',
})

export const FormImageUploader = ({
  onImageUpload,
  onImageDelete,
  onImageDropOrSelected,
  imageOffer,
  disableForm,
  isTemplate,
}: ImageUploaderOfferProps) => (
  <FormLayout.Section
    title="Illustrez votre offre"
    description={
      isTemplate
        ? 'Ajoutez une image pour que votre offre ait 2 fois plus de chances d’être consultée !'
        : ''
    }
  >
    <FormLayout.Row>
      <ImageDragAndDropUploader
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        onImageDropOrSelected={onImageDropOrSelected}
        initialValues={buildInitialValues(imageOffer)}
        mode={UploaderModeEnum.OFFER_COLLECTIVE}
        disabled={disableForm}
      />
    </FormLayout.Row>
  </FormLayout.Section>
)
