import cn from 'classnames'

import { ButtonAppPreview } from './ButtonAppPreview/ButtonAppPreview'
import { ButtonImageDelete } from './ButtonImageDelete/ButtonImageDelete'
import { ButtonImageEdit } from './ButtonImageEdit/ButtonImageEdit'
import { OnImageUploadArgs } from './ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './ButtonImageEdit/types'
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
}

export const ImageUploader = ({
  className,
  onImageUpload,
  onImageDelete,
  initialValues = {},
  mode,
  onClickButtonImageAdd,
  hideActionButtons = false,
}: ImageUploaderProps) => {
  const { imageUrl, originalImageUrl, credit, cropParams } = initialValues

  return (
    <div className={cn(styles['image-uploader-image-container'], className)}>
      {imageUrl && originalImageUrl ? (
        <>
          <img
            alt={'Prévisualisation de l’image'}
            className={cn(styles['image-preview'], {
              [styles['preview-venue'] ?? '']: mode === UploaderModeEnum.VENUE,
              [styles['preview-offer'] ?? '']:
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
                />
                {mode !== UploaderModeEnum.OFFER_COLLECTIVE && (
                  <ButtonAppPreview imageUrl={imageUrl} mode={mode} />
                )}
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
        />
      )}
    </div>
  )
}
