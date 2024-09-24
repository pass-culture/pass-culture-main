import * as Dialog from '@radix-ui/react-dialog'
import { useTranslation } from 'react-i18next'

import { UploaderModeEnum } from 'components/ImageUploader/types'

import { AppPreviewOffer } from '../AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from '../AppPreviewVenue/AppPreviewVenue'

import style from './ModalAppPreview.module.scss'

interface ModalAppPreviewProps {
  mode: UploaderModeEnum
  imageUrl: string
}

export const ModalAppPreview = ({
  mode,
  imageUrl,
}: ModalAppPreviewProps): JSX.Element => {
  const { t } = useTranslation('common')
  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  return (
    <div className={style['container']}>
      <Dialog.Title asChild>
        <h1 className={style['header']}>{t('add_image')}</h1>
      </Dialog.Title>

      <div className={style['subtitle']}>
        Prévisualisation de votre image dans l’application pass Culture
      </div>
      <AppPreview imageUrl={imageUrl} />
    </div>
  )
}
