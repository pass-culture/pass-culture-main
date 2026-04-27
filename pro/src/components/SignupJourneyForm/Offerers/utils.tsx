import type { Dispatch, SetStateAction } from 'react'

import type { Offerer } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'

import styles from './Offerers.module.scss'

const MAX_VENUES_TO_DISPLAY = 3

export function generateVenueDataLines(
  offerer: Offerer | null,
  displayedVenuesNames: string[],
  showAllVenues: boolean,
  setShowAllVenues: Dispatch<SetStateAction<boolean>>
) {
  const showMoreButton = (
    <div className={styles['view-move-button']}>
      <Button
        onClick={() => setShowAllVenues(!showAllVenues)}
        label={
          showAllVenues ? 'Voir moins de structures' : 'Voir plus de structures'
        }
        aria-expanded={showAllVenues}
        size={ButtonSize.SMALL}
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        iconPosition={IconPositionEnum.RIGHT}
        icon={showAllVenues ? fullUpIcon : fullDownIcon}
      />
    </div>
  )

  const venuesToDisplay = showAllVenues
    ? displayedVenuesNames
    : displayedVenuesNames.slice(0, MAX_VENUES_TO_DISPLAY)

  return [
    { label: 'Numéro de SIRET', value: offerer?.siret ?? '' },
    {
      label: pluralizeFr(
        displayedVenuesNames.length,
        'Nom de la structure',
        'Noms des structures'
      ),
      value:
        displayedVenuesNames.length > MAX_VENUES_TO_DISPLAY
          ? [...venuesToDisplay, showMoreButton]
          : venuesToDisplay,
    },
  ]
}
