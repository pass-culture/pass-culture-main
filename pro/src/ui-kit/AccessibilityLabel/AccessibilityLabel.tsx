import cn from 'classnames'
import React from 'react'

import { AccessiblityEnum } from 'core/shared'
import strokeAccessibilityBrain from 'icons/stroke-accessibility-brain.svg'
import audioDisabilitySvg from 'icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEye from 'icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLeg from 'icons/stroke-accessibility-leg.svg'

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
      svg: audioDisabilitySvg,
    },
    [AccessiblityEnum.MENTAL]: {
      label: 'Psychique ou cognitif',
      svg: strokeAccessibilityBrain,
    },
    [AccessiblityEnum.MOTOR]: {
      label: 'Moteur',
      svg: strokeAccessibilityLeg,
    },
    [AccessiblityEnum.VISUAL]: {
      label: 'Visuel',
      svg: strokeAccessibilityEye,
    },
    [AccessiblityEnum.NONE]: {
      label: 'Non accessible',
    },
  }[name]
  return (
    <div className={cn(styles['accessibility-label'], className)}>
      {labelData.svg && <img src={labelData.svg} className={styles['icon']} />}
      <span className={styles['text']}>{labelData.label}</span>
    </div>
  )
}

export default AccessibilityLabel
