import strokeSearchIcon from 'icons/stroke-search.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OffersFavoritesNoResult.module.scss'

export const OffersFavoritesNoResult = () => {
  return (
    <div className={styles['no-results']}>
      <SvgIcon
        src={strokeSearchIcon}
        alt=""
        className={styles['no-results-icon']}
        width="124"
      />
      <p className={styles['no-results-text']}>
        Aucune offre en favoris pour le moment.
      </p>
    </div>
  )
}
