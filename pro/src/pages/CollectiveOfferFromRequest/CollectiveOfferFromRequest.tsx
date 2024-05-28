import { useNavigate, useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import useAnalytics from 'app/App/analytics/firebase'
import { AppLayout } from 'app/AppLayout'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import {
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from 'config/swrQueryKeys'
import { Events } from 'core/FirebaseEvents/constants'
import { createOfferFromTemplate } from 'core/OfferEducational/utils/createOfferFromTemplate'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { Button } from 'ui-kit/Button/Button'
import Spinner from 'ui-kit/Spinner/Spinner'
import { getDateToFrenchText } from 'utils/date'

import styles from './CollectiveOfferFromRequest.module.scss'

export const CollectiveOfferFromRequest = (): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const { offerId, requestId } = useParams<{
    offerId: string
    requestId: string
  }>()

  const { data: offerTemplate } = useSWR(
    () => (offerId ? [GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offerId] : null),
    ([, offerIdParams]) => api.getCollectiveOfferTemplate(Number(offerIdParams))
  )

  const { isLoading, data: informations } = useSWR(
    () =>
      requestId
        ? [GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY, requestId]
        : null,
    ([, id]) => api.getCollectiveOfferRequest(Number(id))
  )

  const handleButtonClick = () => {
    logEvent(Events.CLICKED_CREATE_OFFER_FROM_REQUEST, {
      from: location.pathname,
      requestId,
      templateOfferId: offerId,
    })
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    createOfferFromTemplate(
      navigate,
      notify,
      Number(offerId),
      requestId,
      isMarseilleActive
    )
  }

  return (
    <AppLayout>
      {isLoading || !informations ? (
        <Spinner />
      ) : (
        <>
          <div className={styles['eac-section']}>
            <h1 className={styles['title']}>Récapitulatif de la demande</h1>
          </div>
          <div className={styles['eac-section']}>
            Vous avez reçu une demande de création d’offres de la part d’un
            établissement scolaire. Vous pouvez créer une offre à partir des
            informations saisies par l’enseignant. Toutes les informations sont
            modifiables.
            <br /> L’offre sera visible par l’enseignant sur ADAGE.
          </div>
          <SummarySection title="Détails de la demande">
            <div className={styles['eac-section']}>
              <SummaryDescriptionList
                descriptions={[
                  {
                    title: 'Demande reçue le',
                    text: informations.dateCreated
                      ? getDateToFrenchText(informations.dateCreated)
                      : '-',
                  },
                  {
                    title: 'Offre concernée',
                    text: offerTemplate?.name,
                  },
                ]}
              />
            </div>

            <div className={styles['eac-section']}>
              <SummaryDescriptionList
                descriptions={[
                  {
                    title: 'Etablissement scolaire',
                    text: (
                      <div>
                        {`${informations.institution.institutionType} ${informations.institution.name}`.trim()}
                        <br />
                        {`${informations.institution.postalCode} ${informations.institution.city}`}
                      </div>
                    ),
                  },
                  {
                    title: "Prénom et nom de l'enseignant",
                    text: `${informations.redactor.firstName} ${informations.redactor.lastName}`,
                  },
                  {
                    title: 'Téléphone',
                    text: informations.phoneNumber ?? '-',
                  },
                  {
                    title: 'Email',
                    text: informations.redactor.email,
                  },
                ]}
              />
            </div>

            <SummaryDescriptionList
              descriptions={[
                {
                  title: "Nombre d'élèves",
                  text: informations.totalStudents ?? '-',
                },
                {
                  title: "Nombre d'accompagnateurs",
                  text: informations.totalTeachers ?? '-',
                },
                {
                  title: 'Date souhaitée',
                  text: informations.requestedDate
                    ? getDateToFrenchText(informations.requestedDate)
                    : '-',
                },
                {
                  title: 'Descriptif de la demande',
                  text: informations.comment,
                },
              ]}
            />
          </SummarySection>
          <ActionsBarSticky>
            <ActionsBarSticky.Right>
              <Button onClick={handleButtonClick}>
                Créer l’offre pour l’enseignant
              </Button>
            </ActionsBarSticky.Right>
          </ActionsBarSticky>
        </>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveOfferFromRequest
