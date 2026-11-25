import { useLocation, useNavigate } from 'react-router'

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import strokeLeftIcon from '@/icons/stroke-left.svg'

const IndividualOfferV2TarifModalites = () => {
  const { offer } = useIndividualOfferContext()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')

  const handlePreviousStep = () => {
    navigate(
      getIndividualOfferUrl({
        offerId: offer?.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION_V2,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding,
      })
    )
  }

  return (
    <>
      <FormLayout>
        <FormLayout.Section title="Tarif et modalités">
          <FormLayout.Row>
            Cette étape est en cours de construction.
          </FormLayout.Row>
        </FormLayout.Section>
      </FormLayout>
      <ActionsBarSticky hasSideNav={false} isEmbedded>
        <ActionsBarSticky.Left>
          <Button
            color={ButtonColor.NEUTRAL}
            variant={ButtonVariant.SECONDARY}
            onClick={handlePreviousStep}
            label="Étape précédente"
            icon={strokeLeftIcon}
            iconPosition={IconPositionEnum.LEFT}
          />
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </>
  )
}

// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2TarifModalites
