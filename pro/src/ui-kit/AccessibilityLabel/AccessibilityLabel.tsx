import cn from 'classnames'
import React from 'react'

import { AccessiblityEnum } from 'core/shared'
import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'

import styles from './AccessibilityLabel.module.scss'

interface IAccessibilityLabelProps {
  className?: string
  name: AccessiblityEnum
}

const AccessibilityLabel = ({
  className,
  name,
}: IAccessibilityLabelProps): JSX.Element => {
  const labelData = {
    [AccessiblityEnum.AUDIO]: {
      label: 'Auditif',
      svg: AudioDisabilitySvg,
    },
    [AccessiblityEnum.MENTAL]: {
      label: 'Psychique ou cognitif',
      svg: MentalDisabilitySvg,
    },
    [AccessiblityEnum.MOTOR]: {
      label: 'Moteur',
      svg: MotorDisabilitySvg,
    },
    [AccessiblityEnum.VISUAL]: {
      label: 'Visuel',
      svg: VisualDisabilitySvg,
    },
    [AccessiblityEnum.NONE]: {
      label: 'Non accessible',
    },
  }[name]
  return (
    <div className={cn(styles['accessibility-label'], className)}>
      {labelData.svg && <labelData.svg className={styles['icon']} />}
      <span className={styles['text']}>{labelData.label}</span>
    </div>
  )
}

export default AccessibilityLabel
