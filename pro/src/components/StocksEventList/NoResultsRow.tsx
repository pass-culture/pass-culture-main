import React from 'react'

import searchIcon from 'icons/search-ico.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoResultsRow.module.scss'

interface NoResultsRowProps {
  colSpan: number
}

export const NoResultsRow = ({ colSpan }: NoResultsRowProps) => (
  <tr>
    <td colSpan={colSpan} className={styles['no-data']}>
      <SvgIcon
        src={searchIcon}
        alt=""
        className={styles['no-data-icon']}
        viewBox="0 0 20 20"
      />
      <div className={styles['no-data-message']}>Aucune occurence trouvée</div>
      <div className={styles['no-data-help']}>
        Vous pouvez modifier vos filtres pour lancer une nouvelle recherche
      </div>
    </td>
  </tr>
)
