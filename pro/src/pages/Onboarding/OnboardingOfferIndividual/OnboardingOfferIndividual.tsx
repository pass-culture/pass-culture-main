import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1/models/OfferStatus'
import { GET_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import editFullIcon from 'icons/full-edit.svg'
import connectStrokeIcon from 'icons/stroke-connect.svg'
import { Spinner } from 'ui-kit/Spinner/Spinner'

// import { ActionBar } from '../components/ActionBar/ActionBar'
import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import { CardLink } from './CardLink/CardLink'
import { DraftOffers } from './DraftOffers/DraftOffers'
import styles from './OnboardingOfferIndividual.module.scss'

export const OnboardingOfferIndividual = (): JSX.Element => {
  // const navigate = useNavigate()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offersQuery = useSWR(
    [GET_OFFERS_QUERY_KEY, { status: 'DRAFT' }],
    () => {
      return api.listOffers(
        null,
        selectedOffererId,
        OfferStatus.DRAFT
        // venueId
      )
    },
    { fallbackData: [] }
  )

  if (offersQuery.isLoading) {
    return <Spinner />
  }

  const draftOffers = offersQuery.data
    .filter(({ status }) => status === OfferStatus.DRAFT)
    .slice(0, 50) // Displays 50 draft offers maximum

  return (
    <OnboardingLayout verticallyCentered>
      <h1 className={styles['offers-title']}>Offre à destination des jeunes</h1>
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
              to="/onboarding/synchro"
              icon={connectStrokeIcon}
              label="Automatiquement"
              description="(via mon logiciel de gestion des stocks)"
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

      {/* <ActionBar onLeftButtonClick={() => navigate('/onboarding')} /> */}
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividual
