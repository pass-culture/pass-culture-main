import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1/new'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { GET_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import editFullIcon from '@/icons/full-edit.svg'
import connectStrokeIcon from '@/icons/stroke-connect.svg'
import { CardLink } from '@/ui-kit/CardLink/CardLink'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { DraftOffers } from './DraftOffers/DraftOffers'
import styles from './OnboardingOfferIndividual.module.scss'

export const MAX_DRAFT_TO_DISPLAY = 50

export const OnboardingOfferIndividual = (): JSX.Element => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const offersQuery = useSWR(
    [GET_OFFERS_QUERY_KEY, { status: 'DRAFT' }],
    () => {
      return apiNew.listOffers({
        query: { venueId: selectedPartnerVenue.id, status: OfferStatus.DRAFT },
      })
    },
    { fallbackData: [] }
  )

  if (offersQuery.isLoading) {
    return <Spinner />
  }

  const draftOffers = offersQuery.data.slice(0, MAX_DRAFT_TO_DISPLAY)

  return (
    <OnboardingLayout
      mainHeading="Offre à destination des jeunes"
      verticallyCentered={draftOffers.length <= 1}
      isStickyActionBarInChild
      isEntryScreen
    >
      <h2 className={styles['offers-subtitle']}>
        Comment souhaitez-vous créer votre 1ère offre ?
      </h2>
      <FormLayout>
        <FormLayout.Section>
          <div className={styles['offer-choices']}>
            <CardLink
              to={getIndividualOfferUrl({
                step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                mode: OFFER_WIZARD_MODE.CREATION,
                isOnboarding: true,
              })}
              icon={editFullIcon}
              label="Manuellement"
              direction="vertical"
              className={styles['offer-choice']}
            />

            <CardLink
              to="/parametres"
              icon={connectStrokeIcon}
              label="Automatiquement"
              description="(via mon logiciel de stocks)"
              direction="vertical"
              className={styles['offer-choice']}
            />
          </div>
        </FormLayout.Section>

        {draftOffers.length > 0 && (
          <FormLayout.Section>
            <DraftOffers offers={draftOffers} />
          </FormLayout.Section>
        )}
      </FormLayout>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividual
