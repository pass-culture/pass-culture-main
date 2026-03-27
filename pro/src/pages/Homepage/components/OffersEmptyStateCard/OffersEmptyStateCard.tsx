import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import { OffersEmptyStateCardVariant } from '../types'
import bookableOffers from './assets/bookable-offers.png'
import individualOffers from './assets/individual-offers.png'
import templateOffers from './assets/template-offers.png'
import styles from './OffersEmptyStateCard.module.scss'

const EMPTY_STATE_CONFIG = {
  [OffersEmptyStateCardVariant.BOOKABLE]: {
    title: 'Adresser une offre réservable à un établissement scolaire',
    description:
      'L’offre réservable, datée et tarifée, est destinée à un seul établissement scolaire pour que le projet que vous avez co-construit ensemble puisse se réaliser.',
    buttonLabel: 'Créer une offre réservable',
    to: '/offre/creation/collectif',
    imageSrc: bookableOffers,
  },
  [OffersEmptyStateCardVariant.TEMPLATE]: {
    title:
      'Rendre vos offres visibles à tous les établissements scolaires sur ADAGE',
    description:
      "Les offres vitrines vous permettent de présenter vos propositions aux enseignants afin qu'ils puissent vous contacter pour co-construire des projets d'éducation artistique et culturelle.",
    buttonLabel: 'Créer une offre vitrine',
    to: '/offre/creation/collectif/vitrine',
    imageSrc: templateOffers,
  },
  [OffersEmptyStateCardVariant.INDIVIDUAL]: {
    title: 'Proposer vos offres sur l’application mobile pass Culture',
    description:
      "Les offres individuelles vous permettent de présenter vos propositions culturelles sur l'application.",
    buttonLabel: 'Créer une offre individuelle',
    to: '/offre/individuelle/creation/description',
    imageSrc: individualOffers,
  },
}

export const OffersEmptyStateCard = ({
  variant,
}: {
  variant: OffersEmptyStateCardVariant
}) => {
  const cardContent = EMPTY_STATE_CONFIG[variant]
  return (
    <Card>
      <Card.Image
        src={cardContent.imageSrc}
        alt=""
        className={styles['image']}
      />
      <Card.Header title={cardContent.title} />
      <Card.Content>
        <p>{cardContent.description}</p>
      </Card.Content>
      <Card.Footer>
        <Button
          label={cardContent.buttonLabel}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          to={cardContent.to}
          as="a"
        />
      </Card.Footer>
    </Card>
  )
}
