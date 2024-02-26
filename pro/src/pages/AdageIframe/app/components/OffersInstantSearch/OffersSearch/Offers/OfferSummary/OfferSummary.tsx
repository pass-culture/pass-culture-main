import React from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  OfferAddressType,
} from 'apiClient/adage'
import buildingStrokeIcon from 'icons/stroke-building.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeDateIcon from 'icons/stroke-date.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeLocationIcon from 'icons/stroke-location.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { isCollectiveOfferTemplate } from 'pages/AdageIframe/app/types/offers'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import {
  getRangeToFrenchText,
  toDateStrippedOfTimezone,
  toISOStringWithoutMilliseconds,
} from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

import styles from './OfferSummary.module.scss'

const extractDepartmentCode = (venuePostalCode: string): string => {
  const departmentNumberBase: number = parseInt(venuePostalCode.slice(0, 2))
  if (departmentNumberBase > 95) {
    return venuePostalCode.slice(0, 3)
  } else {
    return venuePostalCode.slice(0, 2)
  }
}

const getLocalBeginningDatetime = (
  beginningDatetime: string,
  venuePostalCode: string | null | undefined
): string => {
  if (!venuePostalCode) {
    return ''
  }

  const departmentCode = extractDepartmentCode(venuePostalCode)
  const stockBeginningDate = new Date(beginningDatetime)
  const stockBeginningDateISOString =
    toISOStringWithoutMilliseconds(stockBeginningDate)
  const stockLocalBeginningDate = formatLocalTimeDateString(
    stockBeginningDateISOString,
    departmentCode,
    'dd/MM/yyyy à HH:mm'
  )

  return stockLocalBeginningDate
}

export type OfferSummaryProps = {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
}

const OfferSummary = ({ offer }: OfferSummaryProps): JSX.Element => {
  const isOfferTemplate = isCollectiveOfferTemplate(offer)
  const { venue, offerVenue, students } = offer
  const { beginningDatetime, numberOfTickets, price } = isOfferTemplate
    ? {
        beginningDatetime: undefined,
        numberOfTickets: undefined,
        price: undefined,
      }
    : offer.stock

  let offerVenueLabel = `${venue.postalCode}, ${venue.city}`

  const formattedDates =
    isCollectiveOfferTemplate(offer) &&
    ((offer.dates?.start &&
      offer.dates?.end &&
      getRangeToFrenchText(
        toDateStrippedOfTimezone(offer.dates.start),
        toDateStrippedOfTimezone(offer.dates.end)
      )) ||
      'Tout au long de l’année scolaire (l’offre est permanente)')

  if (offerVenue) {
    if (offerVenue.addressType === OfferAddressType.OTHER) {
      offerVenueLabel = offerVenue.otherAddress
    } else if (offerVenue.addressType === OfferAddressType.SCHOOL) {
      offerVenueLabel = 'Dans l’établissement scolaire'
    }
  }

  const studentsLabel = students
    ? students?.length > 1
      ? 'Multi niveaux'
      : students[0]
    : ''

  const getFormattedPrice = (price?: number) => {
    if (price === undefined || price === null) {
      return undefined
    }

    return price > 0
      ? new Intl.NumberFormat('fr-FR', {
          style: 'currency',
          currency: 'EUR',
        }).format(price / 100)
      : 'Gratuit'
  }

  const formattedPrice = getFormattedPrice(price)

  return (
    <dl className={styles['offer-summary']}>
      <div className={styles['offer-summary-item']}>
        <>
          <dt>
            <SvgIcon
              alt="Format"
              src={strokeOfferIcon}
              className={styles['offer-summary-item-icon']}
            />
          </dt>
          <dd>{offer.formats?.join(', ')}</dd>
        </>
      </div>
      <div className={styles['offer-summary-item']}>
        <dt>
          <SvgIcon
            alt="Lieu"
            src={strokeLocationIcon}
            className={styles['offer-summary-item-icon']}
            width="20"
          />
        </dt>
        <dd>{offerVenueLabel}</dd>
      </div>
      {formattedDates && (
        <div className={styles['offer-summary-item']}>
          <dt>
            <SvgIcon
              alt=""
              src={strokeCalendarIcon}
              className={styles['offer-summary-item-icon']}
              width="20"
            />
          </dt>
          <dd>{formattedDates}</dd>
        </div>
      )}
      {beginningDatetime && (
        <div className={styles['offer-summary-item']}>
          <dt>
            <SvgIcon
              alt=""
              src={strokeDateIcon}
              className={styles['offer-summary-item-icon']}
              width="20"
            />
          </dt>
          <dd>
            {getLocalBeginningDatetime(beginningDatetime, venue.postalCode)}
          </dd>
        </div>
      )}
      {numberOfTickets && (
        <div className={styles['offer-summary-item']}>
          <dt>
            <SvgIcon
              src={strokeUserIcon}
              alt="Nombre de places"
              className={styles['offer-summary-item-icon']}
              width="20"
            />
          </dt>
          <dd>Jusqu’à {numberOfTickets} places</dd>
        </div>
      )}
      {formattedPrice && (
        <div className={styles['offer-summary-item']}>
          <dt>
            <SvgIcon
              src={strokeEuroIcon}
              alt="Prix"
              className={styles['offer-summary-item-icon']}
              width="20"
            />
          </dt>
          <dd>{formattedPrice}</dd>
        </div>
      )}
      {studentsLabel && (
        <div className={styles['offer-summary-item']}>
          <dt>
            <SvgIcon
              src={buildingStrokeIcon}
              alt="Niveau scolaire"
              className={styles['offer-summary-item-icon']}
              width="20"
            />
          </dt>
          <dd>{studentsLabel}</dd>
        </div>
      )}
    </dl>
  )
}

export default OfferSummary
