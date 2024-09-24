import * as Dialog from '@radix-ui/react-dialog'
import { useTranslation } from 'react-i18next'

import { ImageUploadBrowserForm } from 'components/ImageUploadBrowserForm/ImageUploadBrowserForm'
import { ImageUploadBrowserFormValues } from 'components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import style from './ModalImageUploadBrowser.module.scss'

interface ModalImageUploadBrowserProps {
  onImageClientUpload: (values: ImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
}

export const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
}: ModalImageUploadBrowserProps) => {
  const { t } = useTranslation('common')

  return (
    <section className={style['modal-upload-browser']}>
      <Dialog.Title asChild>
        <h1 className={style['header']}>{t('add_image')}</h1>
      </Dialog.Title>
      <ImageUploadBrowserForm onSubmit={onImageClientUpload} mode={mode} />
    </section>
  )
}
