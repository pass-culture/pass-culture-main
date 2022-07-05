import {
  IOfferAppPreviewProps,
  OfferAppPreview,
} from 'new_components/OfferAppPreview'
import { IOfferSectionProps, OfferSection } from './OfferSection'
import { IStockEventItemProps, StockEventSection } from './StockEventSection'
import { IStockThingSectionProps, StockThingSection } from './StockThingSection'
import { useHistory, useLocation } from 'react-router-dom'

import { ActionBar } from '../ActionBar'
import { BannerSummary } from 'new_components/Banner'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DisplayOfferInAppLink } from 'components/pages/Offers/Offer/DisplayOfferInAppLink'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { ReactComponent as PhoneInfo } from 'icons/info-phone.svg'
import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'
import styles from './Summary.module.scss'

export interface ISummaryProps {
  offerId: string
  formOfferV2?: boolean
  isCreation?: boolean
  offer: IOfferSectionProps
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  preview: IOfferAppPreviewProps
}

const Summary = ({
  formOfferV2 = false,
  isCreation = false,
  offerId,
  offer,
  stockThing,
  stockEventList,
  preview,
}: ISummaryProps): JSX.Element => {
  const location = useLocation()
  const history = useHistory()
  const handleNextStep = () => {
    history.push(`/offre/${offerId}/v3/creation/individuelle/confirmation`)
  }
  const handlePreviousStep = () => {
    history.push(`/offre/${offerId}/v3/creation/individuelle/stocks`)
  }

  return (
    <SummaryLayout>
      <SummaryLayout.Content>
        {isCreation && <BannerSummary />}
        <OfferSection offer={offer} isCreation={isCreation} />
        {stockThing && (
          <StockThingSection
            {...stockThing}
            isCreation={isCreation}
            offerId={offerId}
          />
        )}
        {stockEventList && (
          <StockEventSection
            stocks={stockEventList}
            isCreation={isCreation}
            offerId={offerId}
          />
        )}

        {formOfferV2 ? (
          isCreation && (
            <ButtonLink
              variant={ButtonVariant.PRIMARY}
              to={`/offre/${offerId}/individuel/creation/confirmation${location.search}`}
            >
              Publier
            </ButtonLink>
          )
        ) : (
          <OfferFormLayout.ActionBar>
            <ActionBar
              onClickNext={handleNextStep}
              onClickPrevious={handlePreviousStep}
            />
          </OfferFormLayout.ActionBar>
        )}
      </SummaryLayout.Content>

      <SummaryLayout.Side>
        <div className={styles['offer-creation-preview-title']}>
          <PhoneInfo />
          <span>Aperçu dans l'app</span>
        </div>
        <OfferAppPreview {...preview} />
        {!isCreation && (
          <div className={styles['offer-preview-app-link']}>
            <DisplayOfferInAppLink nonHumanizedId={offer.nonHumanizedId} />
          </div>
        )}
      </SummaryLayout.Side>
    </SummaryLayout>
  )
}

export default Summary
