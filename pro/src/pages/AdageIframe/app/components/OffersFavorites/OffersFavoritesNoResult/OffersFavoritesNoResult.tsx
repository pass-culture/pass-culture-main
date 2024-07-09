import strokeNoFavorite from 'icons/stroke-no-favorite.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OffersFavoritesNoResult.module.scss'

export const OffersFavoritesNoResult = () => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  return (
    <div className={styles['no-results']}>
      <SvgIcon
        src={strokeNoFavorite}
        alt=""
        viewBox="0 0 375 154"
        width="375"
        className={styles['no-results-svg']}
      />
      <div>
        <h2 className={styles['no-results-title']}>
          Vous n’avez pas d’offres en favoris
        </h2>
        <p className={styles['no-results-text']}>
          Explorez le catalogue et ajoutez les offres en favori pour les
          retrouver facilement !
        </p>
        <ButtonLink
          to={`/adage-iframe/recherche?token=${adageAuthToken}`}
          variant={ButtonVariant.PRIMARY}
        >
          Explorer le catalogue
        </ButtonLink>
      </div>
    </div>
  )
}
