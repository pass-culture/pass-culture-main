import cn from 'classnames'
import { useId } from 'react'
import { Link } from 'react-router'

import type { TopOfferResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import strokeSignalIcon from '@/icons/stroke-signal.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './MostViewedOffers.module.scss'

export interface MostViewedOffersProps {
  topOffers: TopOfferResponseModel[]
  hasActiveIndividualOffer: boolean
}

export const MostViewedOffers = ({
  topOffers,
  hasActiveIndividualOffer,
}: MostViewedOffersProps) => {
  const titleId = useId()
  const { logEvent } = useAnalytics()

  return (
    <section
      className={cn(styles.container, {
        [styles['has-empty-state']]:
          !hasActiveIndividualOffer || topOffers.length === 0,
      })}
      aria-labelledby={titleId}
    >
      <p id={titleId} className={styles.title}>
        Top offres
      </p>
      {!hasActiveIndividualOffer || topOffers.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles['empty-state-icon']}>
            <SvgIcon src={strokeSignalIcon} alt="" width="32" />
          </div>
          <p>
            {hasActiveIndividualOffer
              ? 'Vos offres n’ont pas été consultées dernièrement, il est encore temps d’augmenter votre visibilité !'
              : 'Pour rendre visible vos propositions, veuillez publier ou créer au moins une offre.'}
          </p>
        </div>
      ) : (
        <ol className={styles.list}>
          {topOffers.map((topOffer) => (
            <li key={topOffer.offerId} className={styles.item}>
              <Link
                to={getIndividualOfferUrl({
                  offerId: topOffer.offerId,
                  mode: OFFER_WIZARD_MODE.EDITION,
                  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE,
                })}
                className={styles.link}
                onClick={() =>
                  logEvent(HomepageEvents.CLICKED_TOP_OFFER, {
                    from: 'top_offers',
                    offerId: topOffer.offerId,
                  })
                }
              >
                <div
                  className={cn(styles.thumbnail, {
                    [styles['thumbnail-placeholder']]: !topOffer.image?.url,
                  })}
                >
                  {topOffer.image?.url ? (
                    <img
                      src={topOffer.image.url}
                      alt=""
                      aria-hidden="true"
                      loading="lazy"
                    />
                  ) : (
                    <SvgIcon
                      src={strokeOfferIcon}
                      alt=""
                      className={styles['thumbnail-icon']}
                    />
                  )}
                </div>
                <div className={styles.details}>
                  {topOffer.isHeadlineOffer && (
                    <Tag label="À la une" variant={TagVariant.HEADLINE} />
                  )}
                  <span className={styles.name}>{topOffer.name}</span>
                  <span className={styles.views}>
                    {topOffer.views.toLocaleString('fr-FR')}{' '}
                    {pluralizeFr(topOffer.views, 'vue', 'vues')}
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
