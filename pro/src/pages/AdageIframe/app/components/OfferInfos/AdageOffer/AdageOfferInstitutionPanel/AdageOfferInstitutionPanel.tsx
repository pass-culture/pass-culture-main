import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
} from 'apiClient/adage'
import fullDeskIcon from 'icons/full-desk.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { getDateTimeToFrenchText, toDateStrippedOfTimezone } from 'utils/date'

import PrebookingButton from '../../../OffersInstantSearch/OffersSearch/Offers/PrebookingButton/PrebookingButton'
import { getBookableOfferInstitutionAndTeacherName } from '../utils/adageOfferInstitution'

import styles from './AdageOfferInstitutionPanel.module.scss'

export type AdageOfferInstitutionPanelProps = {
  offer: CollectiveOfferResponseModel
  adageUser?: AuthenticatedResponse
  isPreview?: boolean
  setInstitutionOfferCount?: (value: number) => void
  institutionOfferCount?: number
}

export function AdageOfferInstitutionPanel({
  offer,
  adageUser,
  isPreview = false,
  setInstitutionOfferCount,
  institutionOfferCount,
}: AdageOfferInstitutionPanelProps) {
  return (
    <div className={styles['institution-panel']}>
      <div className={styles['institution-panel-header']}>
        <SvgIcon src={strokeTeacherIcon} alt="" width="20" />
        <h2 className={styles['institution-panel-header-title']}>
          Offre adressée à :
        </h2>
      </div>
      <div className={styles['institution-panel-info']}>
        {getBookableOfferInstitutionAndTeacherName(offer)}
      </div>
      <div className={styles['institution-panel-prebooking']}>
        {offer.stock.bookingLimitDatetime && (
          <div className={styles['institution-panel-prebooking-date']}>
            À préréserver{' '}
            <span
              className={styles['institution-panel-prebooking-date-emphasis']}
            >
              avant le{' '}
              {getDateTimeToFrenchText(
                toDateStrippedOfTimezone(offer.stock.bookingLimitDatetime),
                {
                  dateStyle: 'short',
                }
              )}
            </span>
          </div>
        )}
        <PrebookingButton
          canPrebookOffers={
            adageUser?.role === AdageFrontRoles.REDACTOR || isPreview
          }
          offerId={offer.id}
          queryId={''}
          stock={offer.stock}
          hideLimitDate={true}
          isPreview={isPreview}
          setInstitutionOfferCount={setInstitutionOfferCount}
          institutionOfferCount={institutionOfferCount}
        >
          <SvgIcon
            src={fullDeskIcon}
            width="20"
            alt=""
            className={styles['institution-panel-prebooking-icon']}
          />
          Préréserver l’offre
        </PrebookingButton>
      </div>
    </div>
  )
}
