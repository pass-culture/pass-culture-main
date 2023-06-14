import cn from 'classnames'
import React from 'react'

import { AccessiblityEnum } from 'core/shared'
import mentalDisabilitySvg from 'icons/mental-disability.svg'
import motorDisabilitySvg from 'icons/motor-disability.svg'
import audioDisabilitySvg from 'icons/stroke-accessibility-ear.svg'
import visualDisabilitySvg from 'icons/visual-disability.svg'

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
      svg: mentalDisabilitySvg,
    },
    [AccessiblityEnum.MOTOR]: {
      label: 'Moteur',
      svg: motorDisabilitySvg,
    },
    [AccessiblityEnum.VISUAL]: {
      label: 'Visuel',
      svg: visualDisabilitySvg,
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
