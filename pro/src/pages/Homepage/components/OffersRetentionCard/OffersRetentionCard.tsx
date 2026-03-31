import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import { OffersCardVariant } from '../types'

const RETENTION_CONFIG = {
  [OffersCardVariant.TEMPLATE]: {
    title: 'Activités sur vos offres vitrines',
    buttonLabel: 'Créer une offre vitrine',
    to: '/offre/creation/collectif/vitrine',
  },
  [OffersCardVariant.BOOKABLE]: {
    title: 'Activités sur vos offres réservables',
    buttonLabel: 'Créer une offre réservable',
    to: '/offre/creation/collectif',
  },
  [OffersCardVariant.INDIVIDUAL]: {
    title: 'Activités sur vos offres individuelles',
    buttonLabel: 'Créer une offre',
    to: '/offre/individuelle/creation/description',
  },
}

export const OffersRetentionCard = ({
  variant,
}: {
  variant: OffersCardVariant
}) => {
  const config = RETENTION_CONFIG[variant]
  return (
    <Card>
      <Card.Header title={config.title} />
      <Card.Content>
        <Banner title="Vous n’avez plus d’offres actives, souhaitez-vous en créer une nouvelle ?" />
      </Card.Content>
      <Card.Footer>
        <Button
          label={config.buttonLabel}
          variant={ButtonVariant.SECONDARY}
          to={config.to}
          as="a"
        />
      </Card.Footer>
    </Card>
  )
}
