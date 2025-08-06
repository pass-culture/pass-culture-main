import fullMailIcon from '@/icons/full-mail.svg'
import strokeUserIcon from '@/icons/stroke-user.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
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
          <ButtonLink to={`mailto:${contact.email}`} isExternal>
            {contact.email}
          </ButtonLink>
        </dd>
      </div>
    </div>
  )
}
