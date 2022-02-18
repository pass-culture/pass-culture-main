import cn from 'classnames'
import React, { FunctionComponent } from 'react'

import { SubmitButton } from 'ui-kit'

import style from './VenueImagePreview.module.scss'
import { VenuePreviews } from './VenuePreviews/VenuePreviews'

type PropsWithActions = {
  withActions: true
  isUploading: boolean
  onGoBack: () => void
  onUploadImage: () => void
}
type PropsWithoutActions = {
  withActions?: false
  isUploading?: never
  onGoBack?: never
  onUploadImage?: never
}
type Props = (PropsWithActions | PropsWithoutActions) & {
  preview: string
  children?: never
}

export const VenueImagePreview: FunctionComponent<Props> = ({
  preview,
  withActions,
  isUploading,
  onGoBack,
  onUploadImage,
}) => (
  <div className={style['container']}>
    <header>
      <h1 className={style['header']}>Image du lieu</h1>
    </header>
    <div className={style['subtitle']}>
      Prévisualisation de votre image dans l’application pass Culture
    </div>
    <VenuePreviews preview={preview} />
    {withActions && (
      <div className={style['actions']}>
        <button
          className={cn('secondary-button', style['button'])}
          onClick={onGoBack}
          title="Retour"
          type="button"
        >
          Retour
        </button>
        <SubmitButton
          className={style['button']}
          disabled={false}
          isLoading={!!isUploading}
          onClick={onUploadImage}
        />
      </div>
    )}
  </div>
)
