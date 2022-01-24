import React, { FunctionComponent } from 'react'

import style from './ImportFromComputerInput.module.scss'

export type ImportFromComputerInputProps = {
  imageTypes: string[]
  isValid: boolean
  onSetImage: React.ChangeEventHandler<HTMLInputElement>
  children?: never
}

export const ImportFromComputerInput: FunctionComponent<ImportFromComputerInputProps> =
  ({ isValid, imageTypes, onSetImage }) => (
    <label className={'primary-link ' + style['import-from-computer-input']}>
      Importer une image depuis l’ordinateur
      <input
        accept={imageTypes.join()}
        aria-invalid={isValid}
        className={style['import-from-computer-input-file-input']}
        onChange={onSetImage}
        type="file"
      />
    </label>
  )
