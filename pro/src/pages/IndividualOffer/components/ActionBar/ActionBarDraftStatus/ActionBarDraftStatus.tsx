import fullValidateIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ActionBarDraftStatus.module.scss'

type ActionBarDraftStatusProps = {
  isSaved: boolean
}

export function ActionBarDraftStatus({ isSaved }: ActionBarDraftStatusProps) {
  return (
    <>
      {isSaved ? (
        <span className={styles['draft-indicator']}>
          <SvgIcon
            src={fullValidateIcon}
            alt=""
            width="16"
            className={styles['draft-saved-icon']}
          />
          Brouillon enregistré
        </span>
      ) : (
        <span className={styles['draft-indicator']}>
          <div className={styles['draft-not-saved-icon']} />
          Brouillon non enregistré
        </span>
      )}
    </>
  )
}
