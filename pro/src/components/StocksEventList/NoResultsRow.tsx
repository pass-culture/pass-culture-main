
import strokeSearchIcon from 'icons/stroke-search.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoResultsRow.module.scss'

interface NoResultsRowProps {
  colSpan: number
}

export const NoResultsRow = ({ colSpan }: NoResultsRowProps) => (
  <tr>
    <td colSpan={colSpan} className={styles['no-data']}>
      <SvgIcon
        src={strokeSearchIcon}
        alt=""
        className={styles['no-data-icon']}
      />
      <div className={styles['no-data-message']}>Aucune date trouvée</div>
      <div className={styles['no-data-help']}>
        Vous pouvez modifier vos filtres pour lancer une nouvelle recherche
      </div>
    </td>
  </tr>
)
