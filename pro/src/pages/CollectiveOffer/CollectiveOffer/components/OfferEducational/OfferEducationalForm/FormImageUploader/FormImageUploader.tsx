import { OfferCollectiveImage } from 'commons/core/Offers/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { UploadImageValues } from 'components/ImageUploader/components/ButtonImageEdit/types'
import { OnImageUploadArgs } from 'components/ImageUploader/components/ModalImageEdit/ModalImageEdit'
import { ImageUploader } from 'components/ImageUploader/ImageUploader'
import { UploaderModeEnum } from 'components/ImageUploader/types'

export interface ImageUploaderOfferProps {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  imageOffer: OfferCollectiveImage | null
  disableForm: boolean
  isTemplate: boolean
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
