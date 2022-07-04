import {
  IOfferAppPreviewProps,
  OfferAppPreview,
} from 'new_components/OfferAppPreview'
import { IOfferSectionProps, OfferSection } from './OfferSection'
import { IStockEventItemProps, StockEventSection } from './StockEventSection'
import { IStockThingSectionProps, StockThingSection } from './StockThingSection'
import { useHistory, useLocation } from 'react-router-dom'

import { ActionBar } from '../ActionBar'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'
import { SummaryLayout } from 'new_components/SummaryLayout'

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
        <OfferSection {...offer} />
        {stockThing && <StockThingSection {...stockThing} />}
        {stockEventList && <StockEventSection stocks={stockEventList} />}

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
        <OfferAppPreview {...preview} />
      </SummaryLayout.Side>
    </SummaryLayout>
  )
}

export default Summary
