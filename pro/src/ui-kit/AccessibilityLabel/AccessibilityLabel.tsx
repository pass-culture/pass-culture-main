import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import React from 'react'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'
import cn from 'classnames'
import styles from './AccessibilityLabel.module.scss'

export enum AccessiblityLabelEnum {
  Audio = 'audio',
  Mental = 'mental',
  Motor = 'motor',
  Visual = 'visual',
}

interface IAccessibilityLabelProps {
  className?: string
  name: AccessiblityLabelEnum
}

const AccessibilityLabel = ({
  className,
  name,
}: IAccessibilityLabelProps): JSX.Element => {
  const labelData = {
    [AccessiblityLabelEnum.Audio]: {
      label: 'Auditif',
      svg: AudioDisabilitySvg,
    },
    [AccessiblityLabelEnum.Mental]: {
      label: 'Psychique ou cognitif',
      svg: MentalDisabilitySvg,
    },
    [AccessiblityLabelEnum.Motor]: {
      label: 'Moteur',
      svg: MotorDisabilitySvg,
    },
    [AccessiblityLabelEnum.Visual]: {
      label: 'Visuel',
      svg: VisualDisabilitySvg,
    },
  }[name]
  return (
    <div className={cn(styles['accessibility-label'], className)}>
      <labelData.svg className={styles['icon']} />
      <span className={styles['text']}>{labelData.label}</span>
    </div>
  )
}

export default AccessibilityLabel
