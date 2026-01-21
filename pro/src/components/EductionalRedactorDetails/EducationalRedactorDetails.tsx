import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullMailIcon from '@/icons/full-mail.svg'
import strokeUserIcon from '@/icons/stroke-user.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './EducationalRedactorDetails.module.scss'

export interface Contact {
  firstName?: string | null
  lastName?: string | null
  email?: string | null
}

interface EducationalRedactorDetailsProps {
  title: string
  contact: Contact
}

export const EducationalRedactorDetails = ({
  contact,
  title,
}: EducationalRedactorDetailsProps) => {
  return (
    <div className={styles['contact-container']}>
      <div className={styles['contact-title']}>
        <dd>{title}</dd>
      </div>
      <div className={styles['contact-detail']}>
        <dt>
          <SvgIcon
            src={strokeUserIcon}
            alt="Nom"
            className={styles['contact-detail-icon']}
          />
        </dt>
        <dd>{`${contact.firstName} ${contact.lastName}`}</dd>
      </div>

      <div className={styles['contact-detail']}>
        <dt>
          <SvgIcon
            className={styles['contact-detail-icon']}
            alt="Email"
            src={fullMailIcon}
          />
        </dt>
        <dd>
          <Button
            as="a"
            to={`mailto:${contact.email}`}
            isExternal
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
          >
            {contact.email}
          </Button>
        </dd>
      </div>
    </div>
  )
}
