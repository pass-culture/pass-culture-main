import * as Dialog from '@radix-ui/react-dialog'
import { useTranslation } from 'react-i18next'

import { AppPreviewOffer } from 'components/ImageUploader/AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from 'components/ImageUploader/AppPreviewVenue/AppPreviewVenue'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './ModalImageUploadConfirm.module.scss'

interface ModalImageUploadConfirmProps {
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
  const { t } = useTranslation('common')
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
          title={t('back')}
          type="button"
          variant={ButtonVariant.SECONDARY}
        >
          {t('back')}
        </Button>
        <Dialog.Close asChild>
          <Button
            type="submit"
            className={style['button']}
            disabled={false}
            isLoading={!!isUploading}
            onClick={onUploadImage}
          >
            Enregistrer
          </Button>
        </Dialog.Close>
      </div>
    </div>
  )
}
