import cn from 'classnames'
import React, { FunctionComponent } from 'react'

import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import { SubmitButton } from 'ui-kit'

import style from './VenueImageDelete.module.scss'

interface Props {
  onCancel: () => void
  children?: never
}

export const VenueImageDelete: FunctionComponent<Props> = ({ onCancel }) => (
  <div className={style['container']}>
    <div className={style['spacer']} />
    <TrashIcon className={style['icon']} />
    <header>
      <div className={style['header']}>Supprimer l'image</div>
    </header>
    <div className={style['subtitle']}>
      Souhaitez-vous vraiment supprimer cette image ?
    </div>
    <div className={style['actions']}>
      <button
        className={cn('secondary-button', style['button'])}
        onClick={onCancel}
        title="Annuler"
        type="button"
      >
        Retour
      </button>
      <SubmitButton
        className={style['button']}
        disabled={false}
        isLoading={false}
        onClick={() =>
          window.alert('Cette fonctionnalité sera développée par PC-13132')
        }
      >
        Supprimer
      </SubmitButton>
    </div>
  </div>
)
