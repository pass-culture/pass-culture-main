import { useTranslation } from 'react-i18next'

import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndivualOfferLayout } from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'

import { EuropeanOfferConfirmationScreen } from './EuropeanOfferConfirmationScreen'

export const Confirmation = (): JSX.Element => {
  const { t } = useTranslation('common')
  const mode = OFFER_WIZARD_MODE.CREATION

  return (
    <IndivualOfferLayout
      withStepper={false}
      offer={null}
      title={t('create_european_offer')}
      mode={mode}
    >
      <EuropeanOfferConfirmationScreen />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Confirmation
