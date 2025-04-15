import cn from 'classnames'

import { ButtonImageDelete } from './components/ButtonImageDelete/ButtonImageDelete'
import { ButtonImageEdit } from './components/ButtonImageEdit/ButtonImageEdit'
import { UploadImageValues } from './components/ButtonImageEdit/types'
import { OnImageUploadArgs } from './components/ModalImageEdit/ModalImageEdit'
import styles from './ImageUploader.module.scss'
import { UploaderModeEnum } from './types'

export interface ImageUploaderProps {
  className?: string
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onClickButtonImageAdd?: () => void
  hideActionButtons?: boolean
  disableForm?: boolean
}

export const ImageUploader = ({
  className,
  onImageUpload,
  onImageDelete,
  initialValues = {},
  mode,
  onClickButtonImageAdd,
  hideActionButtons = false,
  disableForm = false,
}: ImageUploaderProps) => {
  const { imageUrl, originalImageUrl, credit, cropParams } = initialValues

  return (
    <div className={cn(styles['image-uploader-image-container'], className)}>
      {imageUrl && originalImageUrl ? (
        <>
          <img
            alt={'Prévisualisation de l’image'}
            data-testid="image-preview"
            className={cn(styles['image-preview'], {
              [styles['preview-venue']]: mode === UploaderModeEnum.VENUE,
              [styles['preview-offer']]:
                mode === UploaderModeEnum.OFFER ||
                mode === UploaderModeEnum.OFFER_COLLECTIVE,
            })}
            src={imageUrl}
          />
          {!hideActionButtons && (
            <div className={styles['image-uploader-actions-container']}>
              <div className={styles['actions-wrapper']}>
                <ButtonImageEdit
                  mode={mode}
                  initialValues={{
                    originalImageUrl,
                    imageUrl,
                    credit,
                    cropParams,
                  }}
                  onImageUpload={onImageUpload}
                  onImageDelete={onImageDelete}
                  onClickButtonImage={onClickButtonImageAdd}
                  disableForm={disableForm}
                />

                <ButtonImageDelete onImageDelete={onImageDelete} />
              </div>
            </div>
          )}
        </>
      ) : (
        <ButtonImageEdit
          mode={mode}
          onImageUpload={onImageUpload}
          onImageDelete={onImageDelete}
          onClickButtonImage={onClickButtonImageAdd}
          disableForm={disableForm}
        />
      )}
    </div>
  )
}
