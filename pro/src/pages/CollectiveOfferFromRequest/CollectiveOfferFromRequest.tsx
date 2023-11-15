import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { GetCollectiveOfferRequestResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { SummaryLayout } from 'components/SummaryLayout'
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

const CollectiveOfferFromRequest = (): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const [informations, setInformations] =
    useState<GetCollectiveOfferRequestResponseModel | null>(null)
  const [offerTemplate, setOfferTemplate] = useState<CollectiveOfferTemplate>()
  const [isLoading, setIsLoading] = useState(true)

  const isFormatActive = useActiveFeature('WIP_ENABLE_FORMAT')

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
    createOfferFromTemplate(
      navigate,
      notify,
      Number(offerId),
      isFormatActive,
      requestId
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

    fetchData()
  }, [])

  if (isLoading) {
    return <Spinner />
  }

  return (
    <>
      <div className={styles['eac-section']}>
        <Title level={1}>Récapitulatif de la demande</Title>
      </div>
      <div className={styles['eac-section']}>
        Vous avez reçu une demande de création d'offres de la part d'un
        établissement scolaire. Vous pouvez créer une offre à partir des
        informations saisies par l'enseignant. Toutes les informations sont
        modifiables.
        <br /> L'offre sera visible par l'enseignant sur Adage.
      </div>
      <SummaryLayout.Section title="Détails de la demande">
        <div className={styles['eac-section']}>
          <SummaryLayout.Row
            title="Demande reçue le"
            description={
              informations?.dateCreated
                ? getDateToFrenchText(informations?.dateCreated)
                : '-'
            }
          />
          <SummaryLayout.Row
            title="Offre concernée"
            description={offerTemplate?.name}
          />
        </div>
        <div className={styles['eac-section']}>
          <SummaryLayout.Row
            title="Etablissement scolaire"
            description={
              <div>
                {`${informations?.institution.institutionType} ${informations?.institution.name}`.trim()}
                <br />
                {`${informations?.institution.postalCode} ${informations?.institution.city}`}
              </div>
            }
          />
          <SummaryLayout.Row
            title="Prénom et nom de l'enseignant"
            description={`${informations?.redactor.firstName} ${informations?.redactor.lastName} `}
          />
          <SummaryLayout.Row
            title="Téléphone"
            description={informations?.phoneNumber ?? '-'}
          />
          <SummaryLayout.Row
            title="Email"
            description={informations?.redactor.email}
          />
        </div>

        <SummaryLayout.Row
          title="Nombre d'élèves"
          description={informations?.totalStudents ?? '-'}
        />
        <SummaryLayout.Row
          title="Nombre d'accompagnateurs"
          description={informations?.totalTeachers ?? '-'}
        />
        <SummaryLayout.Row
          title="Date souhaitée"
          description={
            informations?.requestedDate
              ? getDateToFrenchText(informations?.requestedDate)
              : '-'
          }
        />
        <SummaryLayout.Row
          title="Descriptif de la demande"
          description={informations?.comment}
        />
      </SummaryLayout.Section>
      <ActionsBarSticky>
        <ActionsBarSticky.Right>
          <Button onClick={handleButtonClick}>
            Créer l’offre pour l’enseignant
          </Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}

export default CollectiveOfferFromRequest
