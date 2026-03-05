import {
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import fullWaitIcon from '@/icons/full-wait.svg'
import strokePartyIcon from '@/icons/stroke-party.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IndividualOfferTitle.module.scss'

type IndividualOfferTitleProps = {
  mode: OFFER_WIZARD_MODE
  isConfirmationPage: boolean
  offer?: GetIndividualOfferWithAddressResponseModel | null
}

export const IndividualOfferTitle = ({
  mode,
  isConfirmationPage,
  offer,
}: IndividualOfferTitleProps) => {
  if (mode === OFFER_WIZARD_MODE.EDITION) {
    return 'Modifier l’offre'
  } else if (mode === OFFER_WIZARD_MODE.READ_ONLY) {
    return offer?.name
  } else if (!isConfirmationPage) {
    return 'Créer une offre'
  } else if (
    offer?.status === OfferStatus.REJECTED ||
    offer?.status === OfferStatus.PENDING
  ) {
    return (
      <div className={styles['confirmation-title']}>
        Offre en cours de validation{' '}
        <span className={styles['confirmation-title-icon']}>
          <SvgIcon src={fullWaitIcon} alt="" width="38" />
        </span>
      </div>
    )
  } else {
    return (
      <div className={styles['confirmation-title']}>
        Votre offre a été publiée avec succès{' '}
        <span className={styles['confirmation-title-icon']}>
          <SvgIcon src={strokePartyIcon} alt="" width="38" />
        </span>
      </div>
    )
  }
}
