import { useLocation } from 'react-router-dom'

import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

interface WizardModeDetailsList {
  pathPart: string
  mode: OFFER_WIZARD_MODE
}

export const useOfferWizardMode = (): OFFER_WIZARD_MODE => {
  const location = useLocation()

  const modePathMap: WizardModeDetailsList[] = [
    {
      pathPart: 'creation',
      mode: OFFER_WIZARD_MODE.CREATION,
    },
    {
      pathPart: 'edition',
      mode: OFFER_WIZARD_MODE.EDITION,
    },
  ]
  const wizardModeDetails = modePathMap.find((data) =>
    location.pathname.includes(data.pathPart)
  )

  return wizardModeDetails
    ? wizardModeDetails.mode
    : OFFER_WIZARD_MODE.READ_ONLY
}
