import React from 'react'

import { OfferAddressType } from 'apiClient/adage'
import bannerDiscovery from 'icons/banner-discovery-adage.svg'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { defaultCollectiveOffer } from 'utils/adageFactories'

import styles from './AdageDiscovery.module.scss'
import CardOfferComponent, { CardOfferModel } from './CardOffer/CardOffer'
import CardVenue from './CardVenue/CardVenue'

const mockOffer: CardOfferModel = {
  ...defaultCollectiveOffer,
  venue: {
    ...defaultCollectiveOffer.venue,
    distance: 5,
  },
  offerVenue: {
    ...defaultCollectiveOffer.offerVenue,
    distance: 10,
  },
  isTemplate: false,
}

const mockVenue = {
  imageUrl: 'https://picsum.photos/200/300',
  name: 'Le nom administratif du lieu',
  publicName: 'Mon super lieu sur vraiment beaucoup de super lignes',
  distance: 2,
  id: '28',
  city: 'Paris',
}

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
          <div className={styles['section-todo']}>
            <div>TODO: Playlist nouvelle offres publiées à ajouter </div>
            <div className={styles['section-todo-playlist']}>
              <CardOfferComponent
                offer={{
                  ...mockOffer,
                  name: 'Ma super offre',
                  offerVenue: {
                    ...mockOffer.offerVenue,
                    addressType: OfferAddressType.OFFERER_VENUE,
                  },
                  imageUrl: 'https://picsum.photos/201/',
                }}
              />
              <CardOfferComponent
                offer={{
                  ...mockOffer,
                  offerVenue: {
                    ...mockOffer.offerVenue,
                    addressType: OfferAddressType.SCHOOL,
                  },
                  imageUrl: 'https://picsum.photos/202/',
                }}
              />
              <CardOfferComponent
                offer={{
                  ...mockOffer,
                  offerVenue: {
                    ...mockOffer.offerVenue,
                    addressType: OfferAddressType.OTHER,
                  },
                  imageUrl: 'https://picsum.photos/203/',
                }}
              />
            </div>
          </div>
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
          <div className={styles['section-todo']}>
            <div>TODO: Playlist à moins de 30 minutes à pieds à ajouter</div>
            <div className={styles['section-todo-playlist']}>
              <CardVenue venue={mockVenue} />
            </div>
          </div>
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
