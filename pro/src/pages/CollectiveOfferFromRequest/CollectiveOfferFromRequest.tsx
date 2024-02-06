import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { GetCollectiveOfferRequestResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { Events } from 'core/FirebaseEvents/constants'
import {
  CollectiveOfferTemplate,
  createOfferFromTemplate,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { Button, Title } from 'ui-kit'
import Spinner from 'ui-kit/Spinner/Spinner'
import { getDateToFrenchText } from 'utils/date'

import getOfferRequestInformationsAdapter from './adapters/getOfferRequestInformationsAdapter'
import styles from './CollectiveOfferFromRequest.module.scss'

export const CollectiveOfferFromRequest = (): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const [informations, setInformations] =
    useState<GetCollectiveOfferRequestResponseModel | null>(null)
  const [offerTemplate, setOfferTemplate] = useState<CollectiveOfferTemplate>()
  const [isLoading, setIsLoading] = useState(true)

  const isFormatActive = useActiveFeature('WIP_ENABLE_FORMAT')
  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const { offerId, requestId } = useParams<{
    offerId: string
    requestId: string
  }>()

  const handleButtonClick = () => {
    logEvent?.(Events.CLICKED_CREATE_OFFER_FROM_REQUEST, {
      from: location.pathname,
      requestId,
      templateOfferId: offerId,
    })
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    createOfferFromTemplate(
      navigate,
      notify,
      Number(offerId),
      isFormatActive,
      requestId,
      isMarseilleActive
    )
  }

  const fetchOfferTemplateDetails = async () => {
    if (offerId) {
      const { isOk, payload, message } =
        await getCollectiveOfferTemplateAdapter(Number(offerId))
      if (!isOk) {
        return notify.error(message)
      }
      setOfferTemplate(payload)
    } else {
      return notify.error(
        'Une erreur est survenue lors de la récupération de votre offre'
      )
    }
  }

  const getOfferRequestInformation = async () => {
    const { isOk, message, payload } = await getOfferRequestInformationsAdapter(
      Number(requestId)
    )

    if (!isOk) {
      return notify.error(message)
    }
    setInformations(payload)
    setIsLoading(false)
  }

  useEffect(() => {
    const fetchData = async () => {
      await fetchOfferTemplateDetails()
      requestId && (await getOfferRequestInformation())
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    fetchData()
  }, [])

  return (
    <AppLayout>
      {isLoading ? (
        <Spinner />
      ) : (
        <>
          <div className={styles['eac-section']}>
            <Title level={1}>Récapitulatif de la demande</Title>
          </div>
          <div className={styles['eac-section']}>
            Vous avez reçu une demande de création d’offres de la part d’un
            établissement scolaire. Vous pouvez créer une offre à partir des
            informations saisies par l’enseignant. Toutes les informations sont
            modifiables.
            <br /> L’offre sera visible par l’enseignant sur Adage.
          </div>
          <SummarySection title="Détails de la demande">
            <div className={styles['eac-section']}>
              <SummaryRow
                title="Demande reçue le"
                description={
                  informations?.dateCreated
                    ? getDateToFrenchText(informations?.dateCreated)
                    : '-'
                }
              />
              <SummaryRow
                title="Offre concernée"
                description={offerTemplate?.name}
              />
            </div>
            <div className={styles['eac-section']}>
              <SummaryRow
                title="Etablissement scolaire"
                description={
                  <div>
                    {`${informations?.institution.institutionType} ${informations?.institution.name}`.trim()}
                    <br />
                    {`${informations?.institution.postalCode} ${informations?.institution.city}`}
                  </div>
                }
              />
              <SummaryRow
                title="Prénom et nom de l’enseignant"
                description={`${informations?.redactor.firstName} ${informations?.redactor.lastName} `}
              />
              <SummaryRow
                title="Téléphone"
                description={informations?.phoneNumber ?? '-'}
              />
              <SummaryRow
                title="Email"
                description={informations?.redactor.email}
              />
            </div>

            <SummaryRow
              title="Nombre d'élèves"
              description={informations?.totalStudents ?? '-'}
            />
            <SummaryRow
              title="Nombre d'accompagnateurs"
              description={informations?.totalTeachers ?? '-'}
            />
            <SummaryRow
              title="Date souhaitée"
              description={
                informations?.requestedDate
                  ? getDateToFrenchText(informations?.requestedDate)
                  : '-'
              }
            />
            <SummaryRow
              title="Descriptif de la demande"
              description={informations?.comment}
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
