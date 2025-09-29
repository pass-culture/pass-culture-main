import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1/models/OfferStatus'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { GET_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import editFullIcon from '@/icons/full-edit.svg'
import connectStrokeIcon from '@/icons/stroke-connect.svg'
import { CardLink } from '@/ui-kit/CardLink/CardLink'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { DraftOffers } from './DraftOffers/DraftOffers'
import styles from './OnboardingOfferIndividual.module.scss'

export const MAX_DRAFT_TO_DISPLAY = 50

export const OnboardingOfferIndividual = (): JSX.Element => {
  const selectedOfferer = useSelector(selectCurrentOfferer)

  const isNewOfferCreationFlowFFEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const offersQuery = useSWR(
    [GET_OFFERS_QUERY_KEY, { status: 'DRAFT' }],
    () => {
      return api.listOffers(null, selectedOfferer?.id, OfferStatus.DRAFT)
    },
    { fallbackData: [] }
  )

  if (offersQuery.isLoading) {
    return <Spinner />
  }

  const draftOffers = offersQuery.data
    .filter(({ status }) => status === OfferStatus.DRAFT)
    .slice(0, MAX_DRAFT_TO_DISPLAY)

  const physicalVenue = selectedOfferer?.managedVenues?.filter(
    ({ isVirtual }) => !isVirtual
  )[0]

  // Assumed choice to redirect offerers without permanent venues (old cases) to /accueil
  const synchronizedLink = physicalVenue
    ? `/structures/${selectedOfferer.id}/lieux/${physicalVenue.id}/parametres`
    : '/onboarding'

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
        <FormLayout.Section className={styles['form-section']}>
          <div className={styles['offer-choices']}>
            <CardLink
              to={
                isNewOfferCreationFlowFFEnabled
                  ? getIndividualOfferUrl({
                      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
                      mode: OFFER_WIZARD_MODE.CREATION,
                      isOnboarding: true,
                    })
                  : '/onboarding/offre/creation'
              }
              icon={editFullIcon}
              label="Manuellement"
              direction="vertical"
              className={styles['offer-choice']}
            />

            <CardLink
              to={synchronizedLink}
              icon={connectStrokeIcon}
              label="Automatiquement"
              description="(via mon logiciel de stocks)"
              direction="vertical"
              className={styles['offer-choice']}
            />
          </div>
        </FormLayout.Section>

        {draftOffers.length > 0 && (
          <FormLayout.Section className={styles['form-section']}>
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
