import * as Dialog from '@radix-ui/react-dialog'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { AppPreviewOffer } from 'components/ImageUploader/components/ImagePreview/components/AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from 'components/ImageUploader/components/ImagePreview/components/AppPreviewVenue/AppPreviewVenue'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './ModalImageUploadConfirm.module.scss'

export type ModalImageUploadConfirmProps = {
  imageUrl: string
  children?: never
  mode: UploaderModeEnum
  isUploading: boolean
  onGoBack: () => void
  onUploadImage: () => void
}

export const ModalImageUploadConfirm = ({
  imageUrl,
  isUploading,
  onGoBack,
  onUploadImage,
  mode,
}: ModalImageUploadConfirmProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  return (
    <div className={style['container']}>
      <Dialog.Title asChild>
        <h1 className={style['header']}>Modifier une image</h1>
      </Dialog.Title>

      <div className={style['subtitle']}>
        Prévisualisation de votre image dans l’application pass Culture
      </div>
      <AppPreview imageUrl={imageUrl} />

      <div className={style['actions']}>
        <Button
          className={style['button']}
          onClick={onGoBack}
          variant={ButtonVariant.SECONDARY}
        >
          Retour
        </Button>
        <Dialog.Close asChild>
          <Button
            type="submit"
            className={style['button']}
            disabled={false}
            isLoading={!!isUploading}
            onClick={() => {
              logEvent(Events.CLICKED_ADD_IMAGE, {
                imageCreationStage: 'save image',
              })
              onUploadImage()
            }}
          >
            Enregistrer
          </Button>
        </Dialog.Close>
      </div>
    </div>
  )
}
