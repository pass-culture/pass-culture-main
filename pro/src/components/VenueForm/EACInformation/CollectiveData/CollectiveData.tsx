import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { IVenue } from 'core/Venue'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { getInterventionAreaLabels } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/EACInformation/utils/getInterventionAreaLabels'

import styles from './CollectiveData.module.scss'

const CollectiveData = ({ venue }: { venue: IVenue }): JSX.Element => {
  const [culturalPartners, setCulturalPartners] = useState<SelectOption[]>([])
  const notify = useNotification()

  useEffect(() => {
    api
      .getEducationalPartners()
      .then(response => {
        setCulturalPartners(
          response.partners.map(partner => ({
            value: partner.id.toString(),
            label: partner.libelle,
          }))
        )
      })
      .catch(() => {
        notify.error(GET_DATA_ERROR_MESSAGE)
      })
  }, [])

  return (
    <dl>
      {venue.collectiveDescription && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>
            Présentation de vos informations EAC :
          </dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveDescription}
          </dd>
        </div>
      )}

      {venue.collectiveStudents && venue.collectiveStudents?.length > 0 && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>Public cible :</dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveStudents?.join(', ')}
          </dd>
        </div>
      )}

      {venue.collectiveWebsite && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>
            URL de votre site web :
          </dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveWebsite}
          </dd>
        </div>
      )}

      {venue.collectiveDomains && venue.collectiveDomains.length > 0 && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>
            Domaines artistiques et culturels :
          </dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveDomains.map(domain => domain.name).join(', ')}
          </dd>
        </div>
      )}

      {venue.collectiveInterventionArea &&
        venue.collectiveInterventionArea.length > 0 && (
          <>
            <dt className={styles['collective-data-term']}>
              Zone de mobilité :
            </dt>
            <dd className={styles['collective-data-description']}>
              {getInterventionAreaLabels(venue.collectiveInterventionArea)}
            </dd>
          </>
        )}

      {venue.collectiveLegalStatus && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>Statut :</dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveLegalStatus.name}
          </dd>
        </div>
      )}

      {venue.collectiveNetwork && venue.collectiveNetwork.length > 0 && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>
            Réseau partenaire :
          </dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveNetwork
              .map(
                partnerId =>
                  culturalPartners.find(
                    culturalPartner =>
                      partnerId === culturalPartner.value.toString()
                  )?.label
              )
              .join(', ')}
          </dd>
        </div>
      )}

      {venue.collectivePhone && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>Téléphone :</dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectivePhone}
          </dd>
        </div>
      )}

      {venue.collectiveEmail && (
        <div className={styles['collective-data-row']}>
          <dt className={styles['collective-data-term']}>Email :</dt>
          <dd className={styles['collective-data-description']}>
            {venue.collectiveEmail}
          </dd>
        </div>
      )}
    </dl>
  )
}

export default CollectiveData
