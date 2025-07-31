import { FC } from 'react'
import { generatePath, useLocation } from 'react-router'

import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useActiveStep } from 'commons/hooks/useActiveStep'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { Step, StepPattern, Stepper } from 'components/Stepper/Stepper'
import {
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from 'pages/IndividualOffer/commons/filterCategories'
import { NavLinkItems } from 'ui-kit/NavLinkItems/NavLinkItems'

import styles from './IndividualOfferNavigation.module.scss'
import { LabelBooking } from './LabelBooking/LabelBooking'

interface IndividualOfferNavigationProps {
  isUsefulInformationSubmitted: boolean
}

export const IndividualOfferNavigation: FC<IndividualOfferNavigationProps> = ({
  isUsefulInformationSubmitted,
}) => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { offer, isEvent: isEventOfferContext } = useIndividualOfferContext()
  const activeStep = useActiveStep(
    Object.values(INDIVIDUAL_OFFER_WIZARD_STEP_IDS)
  )
  const isMediaPageEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )
  const mode = useOfferWizardMode()
  const hasOffer = offer !== null
  const hasPriceCategories = Boolean(
    offer?.priceCategories && offer.priceCategories.length > 0
  )
  const { search } = useLocation()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')

  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const isEvent =
    isEventOfferContext || offer?.isEvent || isOfferSubtypeEvent(offerSubtype)

  const steps: StepPattern[] = [
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Description'
        : 'Détails de l’offre',
      path: getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
        mode,
        isOnboarding,
      }),
      isActive: true,
    },
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Localisation'
        : 'Informations pratiques',
      path: getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
        mode,
        isOnboarding,
      }),
      isActive: true,
    },
  ]

  if (isMediaPageEnabled) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      label: 'Image et vidéo',
      path: getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
        mode,
        isOnboarding,
      }),
      isActive: true,
    })
  }

  // Intermediate steps depending on isEvent
  if (isEvent) {
    steps.push(
      {
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        label: 'Tarifs',
        path: getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode,
          isOnboarding,
        }),
        isActive:
          (hasOffer && isUsefulInformationSubmitted) || hasPriceCategories,
      },
      {
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
        // This double ternary is temporary while the FF is being rolled out
        label: isNewOfferCreationFlowFeatureActive
          ? 'Horaires'
          : 'Dates & Capacités',
        path: getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          mode,
          isOnboarding,
        }),
        isActive: hasPriceCategories,
      }
    )
  } else {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
      label: isNewOfferCreationFlowFeatureActive ? 'Horaires' : 'Stock & Prix',
      path: getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
        isOnboarding,
      }),
      isActive:
        (hasOffer && isUsefulInformationSubmitted) || Boolean(offer?.hasStocks),
    })
  }

  // Summary/confirmation steps on creation
  if (mode === OFFER_WIZARD_MODE.CREATION) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      label: 'Récapitulatif',
      path: getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
        isOnboarding,
      }),
      isActive: Boolean(offer?.hasStocks),
    })
  }

  if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
      label: <LabelBooking bookingsCount={offer?.bookingsCount || 0} />,
      path: getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        isOnboarding,
      }),
      isActive: true,
    })
  }

  const stepList = steps.map((stepPattern: StepPattern): Step => {
    const step: Step = {
      id: stepPattern.id,
      label: stepPattern.label,
    }
    if (stepPattern.isActive && stepPattern.path && offer) {
      step.url = generatePath(stepPattern.path, {
        offerId: offer.id,
      })
    }
    return step
  })

  return (
    <>
      {mode === OFFER_WIZARD_MODE.CREATION ? (
        <Stepper
          activeStep={activeStep}
          steps={stepList}
          className={styles['stepper']}
        />
      ) : (
        <div className={styles['tabs']}>
          <NavLinkItems
            navLabel="Sous menu - offre individuelle"
            links={stepList.map(({ id, label, url }) => ({
              key: id,
              label,
              url: url || '#',
            }))}
            selectedKey={activeStep}
          />
        </div>
      )}
    </>
  )
}
