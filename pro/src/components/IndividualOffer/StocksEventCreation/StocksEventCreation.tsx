import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { StocksEventList } from 'components/StocksEventList/StocksEventList'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'

import { getDepartmentCode } from '../utils/getDepartmentCode'

import { HelpSection } from './HelpSection/HelpSection'
import styles from './StocksEventCreation.module.scss'

export interface StocksEventCreationProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const StocksEventCreation = ({
  offer,
}: StocksEventCreationProps): JSX.Element => {
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const notify = useNotification()

  const [hasStocks, setHasStocks] = useState<boolean | null>(null)

  const useOffererAddressAsDataSourceEnabled = useActiveFeature(
    'WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE'
  )

  const handlePreviousStep = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
      })
    )
  }

  const handleNextStep = async () => {
    // Check that there is at least one stock left
    if (!hasStocks) {
      notify.error('Veuillez renseigner au moins une date')
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      })
    )
  }

  const departmentCode = getDepartmentCode({
    offer,
    useOffererAddressAsDataSourceEnabled,
  })

  return (
    <>
      <div className={styles['container']}>
        {hasStocks === false && (
          <HelpSection className={styles['help-section']} />
        )}

        <StocksEventList
          priceCategories={offer.priceCategories ?? []}
          departmentCode={departmentCode}
          offer={offer}
          onStocksLoad={setHasStocks}
          canAddStocks
        />
      </div>
      <ActionBar
        isDisabled={false}
        onClickPrevious={handlePreviousStep}
        onClickNext={handleNextStep}
        step={OFFER_WIZARD_STEP_IDS.STOCKS}
        // now we submit in RecurrenceForm, StocksEventCreation could not be dirty
        dirtyForm={false}
      />
    </>
  )
}
