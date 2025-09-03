import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import fullInfoIcon from '@/icons/full-info.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ConnectedAsAside.module.scss'

interface ConnectedAsAsideProps {
  currentUser: SharedCurrentUserResponseModel
}

export const ConnectedAsAside = ({ currentUser }: ConnectedAsAsideProps) => {
  return (
    <aside className={styles['connect-as']}>
      <SvgIcon
        src={fullInfoIcon}
        alt="Information"
        width="20"
        className={styles['connect-as-icon']}
      />
      <div className={styles['connect-as-text']}>
        Vous êtes connecté en tant que :&nbsp;
        <strong>
          {currentUser.firstName} {currentUser.lastName}
        </strong>
      </div>
    </aside>
  )
}
