import { Link } from 'react-router'

import type { OfferHomeResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { StatusLabel } from '@/components/StatusLabel/StatusLabel'
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

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Link className={styles['offer-line-thumb']} to={offerLink}>
        <Thumb url={offer.thumbUrl} alt={`Thumbnail for ${offer.name}`} />
        <span className={styles['visually-hidden']}>Voir l'offre</span>
      </Link>
      <Link className={styles['offer-line-content']} to={offerLink}>
        <IndividualOffersTag
          offer={offer}
          venueDepartmentCode={venueDepartmentCode}
        />
        <div className={styles['offer-line-content-primary']}>{offer.name}</div>
        <div className={styles['offer-line-content-secondary']}>
          {offerLocalDate}
        </div>
      </Link>
      <Link className={styles['offer-line-status']} to={offerLink}>
        <StatusLabel status={offer.status} />
      </Link>
      <IndividualOffersCTA offerId={offer.id} offerStatus={offer.status} />
    </div>
  )
}
