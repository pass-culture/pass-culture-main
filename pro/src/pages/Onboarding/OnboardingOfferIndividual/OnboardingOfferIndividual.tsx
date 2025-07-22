import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1/models/OfferStatus'
import { MainHeading } from 'app/App/layout/Layout'
import { GET_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import editFullIcon from 'icons/full-edit.svg'
import connectStrokeIcon from 'icons/stroke-connect.svg'
import { CardLink } from 'pages/Onboarding/OnboardingOfferIndividual/CardLink/CardLink'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import { DraftOffers } from './DraftOffers/DraftOffers'
import styles from './OnboardingOfferIndividual.module.scss'

export const MAX_DRAFT_TO_DISPLAY = 50

export const OnboardingOfferIndividual = (): JSX.Element => {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { data: offerer, isLoading: isOffererLoading } =
    useOfferer(selectedOffererId)

  const offersQuery = useSWR(
    [GET_OFFERS_QUERY_KEY, { status: 'DRAFT' }],
    () => {
      return api.listOffers(null, selectedOffererId, OfferStatus.DRAFT)
    },
    { fallbackData: [] }
  )

  if (offersQuery.isLoading || isOffererLoading) {
    return <Spinner />
  }

  const draftOffers = offersQuery.data
    .filter(({ status }) => status === OfferStatus.DRAFT)
    .slice(0, MAX_DRAFT_TO_DISPLAY)

  const physicalVenue = offerer?.managedVenues?.filter(
    ({ isVirtual }) => !isVirtual
  )[0]

  // Assumed choice to redirect offerers without permanent venues (old cases) to /accueil
  const synchronizedLink = physicalVenue
    ? `/structures/${selectedOffererId}/lieux/${physicalVenue.id}/parametres`
    : '/onboarding'

  return (
    <OnboardingLayout verticallyCentered={draftOffers.length <= 1}>
      <MainHeading
        mainHeading="Offre à destination des jeunes"
        className={styles['offers-title']}
      />
      <h2 className={styles['offers-subtitle']}>
        Comment souhaitez-vous créer votre 1ère offre ?
      </h2>

      <FormLayout>
        <FormLayout.Section className={styles['form-section']}>
          <div className={styles['offer-choices']}>
            <CardLink
              to="/onboarding/offre/creation"
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
