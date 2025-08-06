import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import strokeBookingHoldIcon from '@/icons/stroke-booking-hold.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IncomeNoData.module.scss'

type IncomeNoDataProps = {
  type: 'venues' | 'income' | 'income-year'
}

export const IncomeNoData = ({ type }: IncomeNoDataProps) => {
  const { logEvent } = useAnalytics()
  const noDataAtAll = type === 'venues' || type === 'income'

  return (
    <div className={styles['income-no-data']}>
      <SvgIcon
        className={styles['income-no-data-icon']}
        src={strokeBookingHoldIcon}
        alt=""
        width="128"
      />
      {!noDataAtAll ? (
        <>
          Vous n’avez aucune réservation sur cette période
          <div className={styles['income-no-data-text-with-link']}>
            Découvrez nos
            <ButtonLink
              isExternal
              opensInNewTab
              to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
              className={styles['income-no-data-text-with-link-buttonlink']}
              onClick={() =>
                logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
                  from: location.pathname,
                })
              }
            >
              Bonnes pratiques & Études
            </ButtonLink>
            pour optimiser la visibilité de vos offres.
          </div>
        </>
      ) : (
        'Vous n’avez aucune réservation pour le moment'
      )}
    </div>
  )
}
