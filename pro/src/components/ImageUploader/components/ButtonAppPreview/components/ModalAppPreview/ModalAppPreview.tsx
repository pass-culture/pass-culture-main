import * as Dialog from '@radix-ui/react-dialog'

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
  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  return (
    <div className={style['container']}>
      <Dialog.Title asChild>
        <h1 className={style['header']}>Ajouter une image</h1>
      </Dialog.Title>
      <AppPreview imageUrl={imageUrl} />
    </div>
  )
}
