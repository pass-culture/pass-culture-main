import React from 'react'

import bannerDiscovery from 'icons/banner-discovery-adage.svg'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './AdageDiscovery.module.scss'

export const AdageDiscovery = () => {
  return (
    <div className={styles['discovery']}>
      <img
        src={bannerDiscovery}
        alt="Bannière pour la découverte"
        width="100%"
      />
      <div className={styles['discovery-playlist']}>
        <div>
          <h1 className={styles['section-title']}>
            Les nouvelles offres publiées
          </h1>
          <div>TODO: Playlist nouvelle offres publiées à ajouter </div>
        </div>
        <div>
          <h1 className={styles['section-title']}>
            Explorez les domaines artistiques
          </h1>
          <div> TODO: Playlist domaines artistiques à ajouter</div>
        </div>
        <div>
          <h1 className={styles['section-title']}>
            Ces interventions peuvent avoir lieu dans votre classe
          </h1>
          <div>TODO: Playlist intervention à ajouter</div>
        </div>
        <div>
          <h1 className={styles['section-title']}>
            À moins de 30 minutes à pieds
          </h1>
          <div>TODO: Playlist à moins de 30 minutes à pieds à ajouter</div>
        </div>
      </div>
      <div className={styles['suggestion']}>
        <h1 className={styles['section-title']}>
          Une idée de rubrique ? Soumettez-la nous !
        </h1>
        <ButtonLink
          className={styles['footer-link']}
          variant={ButtonVariant.TERNARYPINK}
          link={{
            to: '#', // TODO:  Lien FAQ à ajouter quand il sera disponible
            isExternal: true,
          }}
          icon={fullLinkIcon}
        >
          Proposer une idée
        </ButtonLink>
      </div>
    </div>
  )
}
