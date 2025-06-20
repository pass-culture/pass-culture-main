import { EducationalInstitutionResponseModel, CollectiveBookingEducationalRedactorResponseModel } from 'apiClient/v1'
import strokeLocationIcon from 'icons/stroke-location.svg'
import strokeMailIcon from 'icons/stroke-mail.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './EducationalInstitutionDetails.module.scss'

interface EducationalRedactorDetailsProps {
    educationalRedactor: CollectiveBookingEducationalRedactorResponseModel
}

const EducationalRedactorDetails = ({ educationalRedactor }: EducationalRedactorDetailsProps) => {
    return (
        <>
            <div className={styles['contact-detail']}>
                <dt>
                    <SvgIcon
                        src={strokeUserIcon}
                        alt="Nom"
                        className={styles['contact-detail-icon']} />
                </dt>
                <dd>{`${educationalRedactor.firstName} ${educationalRedactor.lastName}`}</dd>
            </div>

            <div className={styles['contact-detail']}>
                <dt>
                    <SvgIcon
                        className={styles['contact-detail-icon']}
                        alt="Email"
                        src={strokeMailIcon} />
                </dt>
                <dd>
                    <ButtonLink
                        to={`mailto:${educationalRedactor.email}`}
                        isExternal
                    >
                        {educationalRedactor.email}
                    </ButtonLink>
                </dd>
            </div>
        </>)
}

export interface EducationalInstitutionDetailsProps {
    educationalInstitution: EducationalInstitutionResponseModel
    educationalRedactor?: CollectiveBookingEducationalRedactorResponseModel | null
    newLayout?: boolean
}

export const EducationalInstitutionDetails = ({ educationalInstitution, educationalRedactor, newLayout = false }: EducationalInstitutionDetailsProps) => {
    return <div>
        <div className={newLayout ? styles['contact-details-container-newlayout'] : styles['contact-details-container-oldlayout']}>
            <div className={newLayout ? styles['contact-details-title-newlayout'] : styles['contact-details-title-oldlayout']}>
                Contact de l’établissement {newLayout ? '' : 'scolaire'}
            </div>
            <dl className={newLayout ? styles['contact-details-newlayout'] : undefined}>
                <div className={styles['contact-detail']}>
                    <dt className={styles['contact-detail-location-icon']}>
                        <SvgIcon
                            className={styles['contact-detail-icon']}
                            alt="Adresse de l’établissement"
                            src={strokeLocationIcon} />
                    </dt>
                    <dd>
                        {`${educationalInstitution.institutionType} ${educationalInstitution.name}`.trim()}
                        <br />
                        {`${educationalInstitution.postalCode} ${educationalInstitution.city}`}
                    </dd>
                </div>

                <div className={styles['contact-detail']}>
                    <dt>
                        <SvgIcon
                            className={styles['contact-detail-icon']}
                            alt="Téléphone"
                            src={strokePhoneIcon} />
                    </dt>
                    <dd>{educationalInstitution.phoneNumber}</dd>
                </div>

                {educationalRedactor && <EducationalRedactorDetails educationalRedactor={educationalRedactor} />}
            </dl>
        </div>
    </div >
}
