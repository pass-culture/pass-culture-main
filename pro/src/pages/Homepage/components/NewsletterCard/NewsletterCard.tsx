import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import newsletter from './assets/newsletter.svg'
import styles from './NewsletterCard.module.scss'

export const NewsletterCard = () => {
  return (
    <Card variant="info">
      <img
        className={styles['newsletter-image']}
        src={newsletter}
        alt=""
        aria-hidden="true"
      />
      <Card.Header
        title="Suivez notre actualité !"
        subtitle="Renseignez votre adresse mail pour recevoir les actualités du pass
          Culture."
      />
      <Card.Footer>
        <Button
          label="S’abonner à la newsletter"
          variant={ButtonVariant.SECONDARY}
          transparent
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          to="https://04a7f3c7.sibforms.com/serve/MUIFAPpqRUKo_nexWvrSwpAXBv-P4ips11dOuqZz5d5FnAbtVD5frxeX6yLHjJcPwiiYAObkjhhcOVTlTkrd7XZDk6Mb2pbWTeaI-BUB6GK-G1xdra_mo-D4xAQsX5afUNHKIs3E279tzr9rDkHn3zVhIHZhcY14BiXhobwL6aFlah1-oXmy_RbznM0dtxVdaWHBPe2z0rYudrUw"
          as="a"
          isExternal
          opensInNewTab
        />
      </Card.Footer>
    </Card>
  )
}
