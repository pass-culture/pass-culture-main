import cn from 'classnames'

import { SvgIcon } from '../SvgIcon/SvgIcon'
import styles from './InfoPanel.module.scss'
import { type InfoPanelProps, InfoPanelSize } from './types'

export const InfoPanel = ({
  title,
  children,
  surface,
  size = InfoPanelSize.LARGE,
  icon,
  iconAlt,
  stepNumber,
}: InfoPanelProps): JSX.Element => {
  const hasStepNumber = stepNumber !== undefined

  return (
    <section
      className={cn(
        styles[`infopanel`],
        styles[`infopanel-${surface}`],
        styles[`infopanel-${size}`]
      )}
    >
      <div
        className={cn(styles['infopanel-left-wrapper'], {
          [styles['infopanel-left-wrapper-icon']]: icon,
          [styles['infopanel-left-wrapper-stepnumber']]: hasStepNumber,
        })}
      >
        {icon && (
          <SvgIcon
            src={icon}
            alt={iconAlt}
            className={styles['infopanel-icon']}
          />
        )}

        {hasStepNumber && stepNumber}
      </div>

      <div className={styles['infopanel-content-wrapper']}>
        <h3 className={styles['infopanel-title']}>{title}</h3>
        <p className={styles['infopanel-content']}>{children}</p>
      </div>
    </section>
  )
}
