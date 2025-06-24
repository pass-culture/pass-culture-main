import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import { EducationalInstitutionDetails } from 'components/EducationalInstitutionDetails/EducationalInstititutionDetails'

import styles from './BookingOfferSummary.module.scss'

export type BookableOfferSummaryProps = {
  offer: GetCollectiveOfferResponseModel
}

export const BookableOfferSummary = ({ offer }: BookableOfferSummaryProps) => {
  const { institution } = offer
  const educationalRedactor = offer.booking?.educationalRedactor
  const teacher = offer.teacher

  return (
    <Layout layout={'sticky-actions'}>
      <div className={styles['container']}>
        <div>
          <p>
            Nouveau composant de recap pour une offre réservable : Work in
            progress
          </p>
          <p>{offer.name}</p>
        </div>
        {/* FIXME: this should be offer.booking.educationalRedactor instead of null*/}
        {institution && <EducationalInstitutionDetails educationalInstitution={institution} educationalRedactor={educationalRedactor} teacher={teacher} newLayout />}
      </div>
    </Layout>
  )
}
