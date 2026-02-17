import cn from 'classnames'

import { SvgIcon } from '../SvgIcon/SvgIcon'
import styles from './InfoPanel.module.scss'
import { type InfoPanelProps, InfoPanelSize, InfoPanelSurface } from './types'

export const InfoPanel = (props: InfoPanelProps): JSX.Element => {
  const { title, children, surface, size = InfoPanelSize.LARGE } = props

  return (
    <section
      className={cn(
        styles[`infopanel`],
        styles[`infopanel-${surface}`],
        styles[`infopanel-${size}`]
      )}
    >
      {surface === InfoPanelSurface.FLAT && (
        <div
          className={cn(
            styles['infopanel-left-wrapper'],
            styles['infopanel-left-wrapper-icon']
          )}
        >
          <SvgIcon
            src={props.icon}
            alt={props.iconAlt}
            className={styles['infopanel-icon']}
          />
        </div>
      )}
      {surface === InfoPanelSurface.ELEVATED && (
        <div
          className={cn(
            styles['infopanel-left-wrapper'],
            styles['infopanel-left-wrapper-stepnumber']
          )}
        >
          {props.stepNumber}
        </div>
      )}
      <div className={styles['infopanel-content-wrapper']}>
        <h3 className={styles['infopanel-title']}>{title}</h3>
        <p className={styles['infopanel-content']}>{children}</p>
      </div>
    </section>
  )
}
