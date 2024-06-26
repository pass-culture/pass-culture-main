import cn from 'classnames'
import { useNavigate } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Step, Stepper } from 'components/Stepper/Stepper'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from 'core/OfferEducational/utils/createOfferFromTemplate'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import fullShowIcon from 'icons/full-show.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Divider } from 'ui-kit/Divider/Divider'
import { Tabs } from 'ui-kit/Tabs/Tabs'

import styles from './CollectiveOfferNavigation.module.scss'

export enum CollectiveOfferStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
  PREVIEW = 'preview',
}

export interface CollectiveOfferNavigationProps {
  activeStep: CollectiveOfferStep
  isCreatingOffer: boolean
  isCompletingDraft?: boolean
  offerId?: number
  className?: string
  isTemplate: boolean
  requestId?: string | null
}

export const CollectiveOfferNavigation = ({
  activeStep,
  isCreatingOffer,
  isTemplate = false,
  isCompletingDraft = false,
  offerId = 0,
  className,
  requestId = null,
}: CollectiveOfferNavigationProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const navigate = useNavigate()

  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const previewLink = `/offre/${computeURLCollectiveOfferId(
    offerId,
    isTemplate
  )}/collectif${isTemplate ? '/vitrine' : ''}/apercu`

  const isEditingExistingOffer = !(isCreatingOffer || isCompletingDraft)

  const stepList: { [key in CollectiveOfferStep]?: Step } = {}

  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  if (!isEditingExistingOffer) {
    stepList[CollectiveOfferStep.DETAILS] = {
      id: CollectiveOfferStep.DETAILS,
      label: 'Détails de l’offre',
    }
    if (!isTemplate) {
      stepList[CollectiveOfferStep.STOCKS] = {
        id: CollectiveOfferStep.STOCKS,
        label: 'Dates et prix',
        url: offerId ? `/offre/${offerId}/collectif/stocks${requestIdUrl}` : '',
      }
      stepList[CollectiveOfferStep.VISIBILITY] = {
        id: CollectiveOfferStep.VISIBILITY,
        label: 'Établissement et enseignant',
      }
    }
    stepList[CollectiveOfferStep.SUMMARY] = {
      id: CollectiveOfferStep.SUMMARY,
      label: 'Récapitulatif',
    }
    stepList[CollectiveOfferStep.PREVIEW] = {
      id: CollectiveOfferStep.PREVIEW,
      label: 'Aperçu',
    }
    stepList[CollectiveOfferStep.CONFIRMATION] = {
      id: CollectiveOfferStep.CONFIRMATION,
      label: 'Confirmation',
    }
  }

  //  Steps witout url will be displayed as disabeld in the stepper,
  //  that's why we need to add url only to the current step and the previeous steps

  // Add clickable urls depending on current completion
  // Switch fallthrough is intended, this is precisely the kind of use case for it
  /* eslint-disable no-fallthrough */
  switch (activeStep) {
    // @ts-expect-error switch fallthrough
    case CollectiveOfferStep.CONFIRMATION:
      if (stepList[CollectiveOfferStep.PREVIEW]) {
        stepList[CollectiveOfferStep.PREVIEW].url = isTemplate
          ? `/offre/${offerId}/collectif/vitrine/creation/apercu`
          : `/offre/${offerId}/collectif/creation/apercu`
      }

    // @ts-expect-error switch fallthrough
    case CollectiveOfferStep.PREVIEW:
      if (stepList[CollectiveOfferStep.SUMMARY]) {
        stepList[CollectiveOfferStep.SUMMARY].url = isTemplate
          ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
          : `/offre/${offerId}/collectif/creation/recapitulatif`
      }

    // @ts-expect-error switch fallthrough
    case CollectiveOfferStep.SUMMARY:
      if (!isTemplate && stepList[CollectiveOfferStep.VISIBILITY]) {
        stepList[CollectiveOfferStep.VISIBILITY].url =
          `/offre/${offerId}/collectif/visibilite`
      }

    // @ts-expect-error switch fallthrough
    case CollectiveOfferStep.VISIBILITY:
      if (!isTemplate && stepList[CollectiveOfferStep.STOCKS]) {
        stepList[CollectiveOfferStep.STOCKS].url =
          `/offre/${offerId}/collectif/stocks`
      }

    // @ts-expect-error switch fallthrough
    case CollectiveOfferStep.STOCKS:
      if (stepList[CollectiveOfferStep.DETAILS]) {
        stepList[CollectiveOfferStep.DETAILS].url = isTemplate
          ? `/offre/collectif/vitrine/${offerId}/creation`
          : `/offre/collectif/${offerId}/creation${requestIdUrl}`
      }

    case CollectiveOfferStep.DETAILS:
    // Nothing to do here
  }

  const steps = Object.values(stepList)
  const tabs = steps.map(({ id, label, url }) => ({
    key: id,
    label,
    url,
  }))

  return isEditingExistingOffer ? (
    <>
      <div className={styles['duplicate-offer']}>
        <ButtonLink
          link={{
            to: previewLink,
            isExternal: false,
          }}
          icon={fullShowIcon}
        >
          Aperçu dans ADAGE
        </ButtonLink>
        {isTemplate && (
          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullMoreIcon}
            onClick={() => {
              logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
                from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
              })
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              createOfferFromTemplate(
                navigate,
                notify,
                offerId,
                undefined,
                isMarseilleActive
              )
            }}
          >
            Créer une offre réservable
          </Button>
        )}
      </div>
      <Divider />
      <Tabs
        tabs={tabs}
        selectedKey={activeStep}
        className={cn(styles['tabs'], {
          [styles['tabs-active']]: [
            CollectiveOfferStep.DETAILS,
            CollectiveOfferStep.STOCKS,
            CollectiveOfferStep.VISIBILITY,
          ].includes(activeStep),
        })}
      />
    </>
  ) : (
    <Stepper activeStep={activeStep} className={className} steps={steps} />
  )
}
