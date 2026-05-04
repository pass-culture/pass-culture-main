import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import strokeBookingHoldIcon from '@/icons/stroke-hide.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IncomeNoData.module.scss'

type IncomeNoDataProps = {
  type: 'venues' | 'income' | 'income-year' | 'no-venues-selected'
}

export const IncomeNoData = ({ type }: IncomeNoDataProps) => {
  const { logEvent } = useAnalytics()

  const renderContent = () => {
    switch (type) {
      case 'venues':
      case 'income':
        return "Aucun remboursement n'a été effectué"

      case 'no-venues-selected':
        return 'Vous devez sélectionner au moins un partenaire'

      case 'income-year':
        return (
          <>
            Vous n’avez aucune réservation sur cette période
            <div className={styles['income-no-data-text-with-link']}>
              Découvrez nos{' '}
              <span
                className={styles['income-no-data-text-with-link-buttonlink']}
              >
                <Button
                  as="a"
                  isExternal
                  opensInNewTab
                  to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  onClick={() =>
                    logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
                      from: location.pathname,
                    })
                  }
                  label="Bonnes pratiques & Études"
                />
              </span>{' '}
              pour optimiser la visibilité de vos offres.
            </div>
          </>
        )

      default:
        return null
    }
  }

  return (
    <div className={styles['income-no-data']}>
      <SvgIcon
        className={styles['income-no-data-icon']}
        src={strokeBookingHoldIcon}
        alt=""
        width="48"
      />
      {renderContent()}
    </div>
  )
}
