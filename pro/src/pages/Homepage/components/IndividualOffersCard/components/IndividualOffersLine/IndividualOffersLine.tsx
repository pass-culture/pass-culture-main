import { Link } from 'react-router'

import type { OfferHomeResponseModel } from '@/apiClient/v1/new'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import {
  OFFER_STATUS_PROPERTIES,
  StatusLabel,
} from '@/components/StatusLabel/StatusLabel'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import { IndividualOffersCTA } from '../IndividualOffersCTA/IndividualOffersCTA'
import { IndividualOffersTag } from '../IndividualOffersTag/IndividualOffersTag'
import styles from './IndividualOffersLine.module.scss'

type IndividualOffersLineProps = {
  offer: OfferHomeResponseModel
  venueDepartmentCode: string | null
}

function getOfferLocalDate(
  offer: OfferHomeResponseModel,
  venueDepartmentCode: string | null
): string {
  if (!offer.isEvent || offer.stocks.length === 0) {
    return ''
  }
  if (offer.stocks.length === 1) {
    if (!offer.stocks[0].beginningDatetime) {
      return ''
    }

    const departmentCode = (offer.departmentCode || venueDepartmentCode) ?? ''

    const dateToDisplay = formatLocalTimeDateString(
      offer.stocks[0].beginningDatetime,
      departmentCode,
      FORMAT_DD_MM_YYYY_HH_mm
    )
    return `Le ${dateToDisplay}`
  }
  return `${offer.stocks.length} dates`
}

export const IndividualOffersLine = ({
  offer,
  venueDepartmentCode,
}: IndividualOffersLineProps): JSX.Element => {
  const offerLink = getIndividualOfferUrl({
    offerId: offer.id,
    mode: OFFER_WIZARD_MODE.READ_ONLY,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
  })

  const offerLocalDate = getOfferLocalDate(offer, venueDepartmentCode)
  const bookingsLabel = `${offer.bookingsCount} ${pluralizeFr(offer.bookingsCount, 'réservation', 'réservations')}`

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Thumb
        className={styles['offer-line-thumb']}
        url={offer.thumbUrl}
        alt={`Thumbnail for ${offer.name}`}
      />
      <div className={styles['offer-line-content']}>
        <IndividualOffersTag
          offer={offer}
          venueDepartmentCode={venueDepartmentCode}
        />
        <h4 className={styles['offer-line-content-primary']}>
          <Link
            className={styles['offer-line-link']}
            to={offerLink}
            aria-label={[
              bookingsLabel,
              offer.name,
              offerLocalDate,
              OFFER_STATUS_PROPERTIES[offer.status]?.label,
            ]
              .filter(Boolean)
              .join(' - ')}
          >
            {offer.name}
          </Link>
        </h4>
        <div className={styles['offer-line-content-secondary']}>
          {offerLocalDate}
        </div>
      </div>
      <div className={styles['offer-line-status']}>
        <StatusLabel status={offer.status} />
      </div>
      <IndividualOffersCTA offerId={offer.id} offerStatus={offer.status} />
    </div>
  )
}
