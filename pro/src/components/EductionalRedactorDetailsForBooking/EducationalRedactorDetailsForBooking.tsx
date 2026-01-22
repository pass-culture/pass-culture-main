import type { Contact } from '@/components/EductionalRedactorDetails/EducationalRedactorDetails'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import strokeMailIcon from '@/icons/stroke-mail.svg'
import strokeUserIcon from '@/icons/stroke-user.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './EducationalRedactorDetailsForBooking.module.scss'

interface EducationalRedactorDetailsForBookingProps {
  contact: Contact
}

export const EducationalRedactorDetailsForBooking = ({
  contact,
}: EducationalRedactorDetailsForBookingProps) => {
  return (
    <>
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
            className={styles['contact-redactor-icon']}
            alt="Email"
            src={strokeMailIcon}
          />
        </dt>
        <dd>
          <Button
            as="a"
            to={`mailto:${contact.email}`}
            isExternal
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            label={contact.email ?? ''}
          />
        </dd>
      </div>
    </>
  )
}
