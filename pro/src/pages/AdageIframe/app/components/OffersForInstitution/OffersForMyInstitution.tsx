import useSWR from 'swr'

import { AdageFrontRoles } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import {
  GET_COLLECTIVE_OFFERS_FOR_INSTITUTION_QUERY_KEY,
  GET_EDUCATIONAL_INSTITUTION_BUDGET_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import strokeMyInstitution from '@/icons/stroke-my-institution.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { useAdageUser } from '../../hooks/useAdageUser'
import { AdageBudgetInformationBanner } from '../AdageBudgetInformationBanner/AdageBudgetInformationBanner'
import { AdageOfferListCard } from '../OffersInstantSearch/OffersSearch/Offers/AdageOfferListCard/AdageOfferListCard'
import { AdageSkeleton } from '../Skeleton/AdageSkeleton'
import styles from './OffersForMyInstitution.module.scss'

export const OffersForMyInstitution = () => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')
  const { adageUser } = useAdageUser()

  const { data: offers, isLoading } = useSWR(
    [GET_COLLECTIVE_OFFERS_FOR_INSTITUTION_QUERY_KEY],
    () => apiAdage.getCollectiveOffersForMyInstitution(),
    { fallbackData: { collectiveOffers: [] } }
  )

  const educationalInstitutionBudget = useSWR(
    adageUser.role !== AdageFrontRoles.READONLY
      ? GET_EDUCATIONAL_INSTITUTION_BUDGET_QUERY_KEY
      : null,
    () => apiAdage.getEducationalInstitutionWithBudget()
  )
  const budget = educationalInstitutionBudget.data?.budget

  if (isLoading) {
    return (
      <>
        <AdageSkeleton />
        <AdageSkeleton />
        <AdageSkeleton />
      </>
    )
  }

  return (
    <>
      <h1 className={styles['title']}>Pour mon établissement</h1>
      {!budget && (
        <div className={styles['budget-banner-container']}>
          <AdageBudgetInformationBanner />
        </div>
      )}
      {offers.collectiveOffers.length === 0 ? (
        <div className={styles['no-results']}>
          <SvgIcon
            src={strokeMyInstitution}
            alt=""
            viewBox="0 0 375 154"
            width="375"
            className={styles['no-results-svg']}
          />
          <div>
            <h2 className={styles['no-results-title']}>
              Vous n’avez pas d’offre à préréserver
            </h2>
            <Button
              as="a"
              to={`/adage-iframe/recherche?token=${adageAuthToken}`}
              variant={ButtonVariant.PRIMARY}
              label="Explorer le catalogue"
            />
          </div>
        </div>
      ) : (
        <ul className={styles['offers-list']}>
          {offers.collectiveOffers.map((offer) => {
            return (
              <li key={offer.id} data-testid="offer-listitem">
                <AdageOfferListCard offer={offer} />
              </li>
            )
          })}
        </ul>
      )}
    </>
  )
}
