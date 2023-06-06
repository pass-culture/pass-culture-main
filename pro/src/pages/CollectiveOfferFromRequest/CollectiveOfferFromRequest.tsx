import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { GetCollectiveOfferRequestResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  CollectiveOfferTemplate,
  createOfferFromTemplate,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import useNotification from 'hooks/useNotification'
import { Button, Title } from 'ui-kit'
import Spinner from 'ui-kit/Spinner/Spinner'

import getOfferRequestInformationsAdapter from './adapters/getOfferRequestInformationsAdapter'
import styles from './CollectiveOfferFromRequest.module.scss'

const CollectiveOfferFromRequest = (): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()

  const [informations, setInformations] =
    useState<GetCollectiveOfferRequestResponseModel | null>(null)
  const [offerTemplate, setOfferTemplate] =
    useState<CollectiveOfferTemplate | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const { offerId, requestId } = useParams<{
    offerId: string
    requestId: string
  }>()

  const handleButtonClick = () => {
    createOfferFromTemplate(navigate, notify, Number(offerId))
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
    if (requestId) {
      const { isOk, message, payload } =
        await getOfferRequestInformationsAdapter(Number(requestId))

      if (!isOk) {
        return notify.error(message)
      }
      setInformations(payload)
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOfferTemplateDetails()
    getOfferRequestInformation()
  }, [])

  if (isLoading) {
    return <Spinner />
  }

  return (
    <>
      <div className={styles['eac-heading']}>
        <Title level={1}>Récapitulatif de la demande</Title>
      </div>
      <div className={styles['eac-info']}>
        Vous avez reçu une demande de création d'offres de la part d'un
        établissement scolaire. Vous pouvez créer une offre à partir des
        informations saisies par l'enseignant. Toutes les informations sont
        modifiables.
        <br /> L'offre sera visible par l'enseignant sur Adage.
      </div>
      <SummaryLayout.Section title="Détails de la demande">
        <SummaryLayout.Row
          title="Demande reçue le"
          description="13 août 2022"
        />
        <SummaryLayout.Row
          title="Offre concernée"
          description={offerTemplate?.name ?? '-'}
        />
        <br />
        <SummaryLayout.Row
          title="Etablissement scolaire"
          description={
            <div>
              LYCEE GENERAL ET TECHNOLOGIQUE GEORGES BRASSENS <br />
              40 rue des palfreniers, 75005 Paris
            </div>
          }
        />
        <SummaryLayout.Row
          title="Prénom et nom de l'enseignant"
          description="Alain Provist"
        />
        <SummaryLayout.Row
          title="Téléphone"
          description={informations?.phoneNumber ?? '-'}
        />
        <SummaryLayout.Row title="E-mail" description={informations?.email} />
        <br />
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
          description={informations?.requestedDate ?? '-'}
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
