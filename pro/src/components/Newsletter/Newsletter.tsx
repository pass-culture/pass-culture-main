import fullLinkIcon from '@/icons/full-link.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './Newsletter.module.scss'
import { NewsletterSVG } from './NewsletterSVG'

export const Newsletter = () => {
  return (
    <div className={styles['newsletter-container']}>
      <ButtonLink
        className={styles['newsletter-link']}
        variant={ButtonVariant.TERNARY}
        to="https://04a7f3c7.sibforms.com/serve/MUIFAPpqRUKo_nexWvrSwpAXBv-P4ips11dOuqZz5d5FnAbtVD5frxeX6yLHjJcPwiiYAObkjhhcOVTlTkrd7XZDk6Mb2pbWTeaI-BUB6GK-G1xdra_mo-D4xAQsX5afUNHKIs3E279tzr9rDkHn3zVhIHZhcY14BiXhobwL6aFlah1-oXmy_RbznM0dtxVdaWHBPe2z0rYudrUw"
        isExternal
        opensInNewTab
        icon={fullLinkIcon}
      >
        Inscrivez-vous à notre newsletter pour recevoir les actualités du pass
        Culture
        <NewsletterSVG className={styles['newsletter-img']} />
      </ButtonLink>
    </div>
  )
}
