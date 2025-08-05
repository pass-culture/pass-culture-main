import { Contact } from 'components/EductionalRedactorDetails/EducationalRedactorDetails'
import strokeMailIcon from 'icons/stroke-mail.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
          <ButtonLink to={`mailto:${contact.email}`} isExternal>
            {contact.email}
          </ButtonLink>
        </dd>
      </div>
    </>
  )
}
