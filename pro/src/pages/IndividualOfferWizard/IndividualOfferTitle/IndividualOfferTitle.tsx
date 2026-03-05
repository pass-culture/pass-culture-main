import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

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
  } else if (isConfirmationPage) {
    return undefined
  } else {
    return 'Créer une offre'
  }
}
