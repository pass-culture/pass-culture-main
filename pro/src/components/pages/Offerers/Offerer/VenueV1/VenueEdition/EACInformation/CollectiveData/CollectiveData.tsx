import React, { useEffect, useState } from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { Title } from 'ui-kit'

import { getCulturalPartnersAdapter } from '../../adapters'
import { getInterventionAreaLabels } from '../utils/getInterventionAreaLabels'

import styles from './CollectiveData.module.scss'

const CollectiveData = ({
  venue,
}: {
  venue: GetVenueResponseModel
}): JSX.Element => {
  const [culturalPartners, setCulturalPartners] = useState<SelectOption[]>([])

  useEffect(() => {
    getCulturalPartnersAdapter().then(response => {
      setCulturalPartners(response.payload)
    })
  }, [])

  return (
    <>
      {venue.collectiveDescription && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            Présentation de vos informations EAC :{' '}
          </Title>
          {venue.collectiveDescription}
        </div>
      )}

      {venue.collectiveStudents && venue.collectiveStudents?.length > 0 && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            Public cible :{' '}
          </Title>
          {venue.collectiveStudents?.join(', ')}
        </div>
      )}

      {venue.collectiveWebsite && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            URL de votre site web :{' '}
          </Title>
          {venue.collectiveWebsite}
        </div>
      )}

      {venue.collectiveDomains && venue.collectiveDomains.length > 0 && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            Domaines artistiques et culturels :{' '}
          </Title>
          {venue.collectiveDomains.map(domain => domain.name).join(', ')}
        </div>
      )}

      {venue.collectiveInterventionArea &&
        venue.collectiveInterventionArea.length > 0 && (
          <div className={styles['collective-data-row']}>
            <Title className={styles['collective-data-title']} level={4}>
              Zone de mobilité :{' '}
            </Title>
            {getInterventionAreaLabels(venue.collectiveInterventionArea)}
          </div>
        )}

      {venue.collectiveLegalStatus && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            Statut :{' '}
          </Title>
          <>{venue.collectiveLegalStatus.name}</>
        </div>
      )}

      {venue.collectiveNetwork && venue.collectiveNetwork.length > 0 && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            Réseau partenaire :{' '}
          </Title>
          {venue.collectiveNetwork
            .map(
              partnerId =>
                culturalPartners.find(
                  culturalPartner =>
                    partnerId === culturalPartner.value.toString()
                )?.label
            )
            .join(', ')}
        </div>
      )}

      {venue.collectivePhone && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            Téléphone :{' '}
          </Title>
          {venue.collectivePhone}
        </div>
      )}

      {venue.collectiveEmail && (
        <div className={styles['collective-data-row']}>
          <Title className={styles['collective-data-title']} level={4}>
            E-mail :{' '}
          </Title>
          {venue.collectiveEmail}
        </div>
      )}
    </>
  )
}

export default CollectiveData
