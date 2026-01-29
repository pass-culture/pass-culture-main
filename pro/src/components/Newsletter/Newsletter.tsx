import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './Newsletter.module.scss'
import { NewsletterSVG } from './NewsletterSVG'

export const Newsletter = () => {
  return (
    <div className={styles['newsletter-container']}>
      <Button
        as="a"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        to="https://04a7f3c7.sibforms.com/serve/MUIFAPpqRUKo_nexWvrSwpAXBv-P4ips11dOuqZz5d5FnAbtVD5frxeX6yLHjJcPwiiYAObkjhhcOVTlTkrd7XZDk6Mb2pbWTeaI-BUB6GK-G1xdra_mo-D4xAQsX5afUNHKIs3E279tzr9rDkHn3zVhIHZhcY14BiXhobwL6aFlah1-oXmy_RbznM0dtxVdaWHBPe2z0rYudrUw"
        isExternal
        opensInNewTab
        icon={fullLinkIcon}
        label="Inscrivez-vous à notre newsletter pour recevoir les actualités du pass
        Culture"
      />
      <NewsletterSVG className={styles['newsletter-img']} />
    </div>
  )
}
