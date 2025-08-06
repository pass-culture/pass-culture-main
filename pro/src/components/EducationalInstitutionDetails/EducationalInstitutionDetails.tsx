import { EducationalInstitutionResponseModel } from '@/apiClient/v1'
import {
  Contact,
  EducationalRedactorDetails,
} from '@/components/EductionalRedactorDetails/EducationalRedactorDetails'
import { EducationalRedactorDetailsForBooking } from '@/components/EductionalRedactorDetailsForBooking/EducationalRedactorDetailsForBooking'
import strokePhoneIcon from '@/icons/stroke-phone.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './EducationalInstitutionDetails.module.scss'

export interface EducationalInstitutionDetailsProps {
  educationalInstitution: EducationalInstitutionResponseModel
  educationalRedactor?: Contact | null
  teacher?: Contact | null
  newLayout?: boolean
}

export const EducationalInstitutionDetails = ({
  educationalInstitution,
  educationalRedactor,
  teacher,
  newLayout = false,
}: EducationalInstitutionDetailsProps) => {
  return (
    <div
      className={
        newLayout
          ? styles['contact-details-container-newlayout']
          : styles['contact-details-container-oldlayout']
      }
    >
      <h2
        className={
          newLayout
            ? styles['contact-details-title-newlayout']
            : styles['contact-details-title-oldlayout']
        }
      >
        Contact de l’établissement {newLayout ? '' : 'scolaire'}
      </h2>
      <dl
        className={newLayout ? styles['contact-details-newlayout'] : undefined}
      >
        <div className={styles['contact-detail']}>
          <dd>
            {`${educationalInstitution.institutionType} ${educationalInstitution.name}`.trim()}
            <br />
            {`${educationalInstitution.postalCode} ${educationalInstitution.city}`}
            <br />
            UAI : {educationalInstitution.institutionId}
          </dd>
        </div>

        <div className={styles['contact-detail']}>
          <dt>
            <SvgIcon
              className={styles['contact-detail-icon']}
              alt="Téléphone"
              src={strokePhoneIcon}
            />
          </dt>
          <dd>{educationalInstitution.phoneNumber}</dd>
        </div>

        {newLayout ? (
          <>
            {teacher && (
              <EducationalRedactorDetails
                contact={teacher}
                title="Offre destinée à :"
              />
            )}
            {educationalRedactor && (
              <EducationalRedactorDetails
                contact={educationalRedactor}
                title="Offre préréservée par :"
              />
            )}
          </>
        ) : (
          <>
            {educationalRedactor && (
              <EducationalRedactorDetailsForBooking
                contact={educationalRedactor}
              />
            )}
          </>
        )}
      </dl>
    </div>
  )
}
