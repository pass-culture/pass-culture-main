import cn from 'classnames'

import { SvgIcon } from '../SvgIcon/SvgIcon'
import styles from './InfoPanelList.module.scss'
import {
  type InfoPanelItemProps,
  type InfoPanelListProps,
  InfoPanelSize,
  InfoPanelVariant,
} from './types'

const InfoPanelItem = ({
  variant,
  panel,
  index,
  Heading,
}: InfoPanelItemProps) => {
  return (
    <li className={styles['info-panel-item']}>
      <div className={styles['info-panel-item-left-content']}>
        {variant === InfoPanelVariant.UNORDERED ? (
          <SvgIcon
            src={panel.icon}
            alt={panel.iconAlt}
            className={styles['info-panel-item-icon']}
          />
        ) : (
          <p
            className={styles['info-panel-item-stepnumber']}
            aria-hidden="true"
          >
            {index + 1}
          </p>
        )}
      </div>

      <div className={styles['info-panel-item-content']}>
        <Heading className={styles['info-panel-item-title']}>
          {variant === InfoPanelVariant.ORDERED && (
            <span className={styles['visually-hidden']}>{index + 1} -</span>
          )}
          {panel.title}
        </Heading>
        <p className={styles['info-panel-item-description']}>
          {panel.description}
        </p>
      </div>
    </li>
  )
}

export const InfoPanelList = ({
  variant,
  titleLevel = '3',
  surface,
  size = InfoPanelSize.LARGE,
  panels,
}: Readonly<InfoPanelListProps>): JSX.Element => {
  const List = variant === InfoPanelVariant.ORDERED ? 'ol' : 'ul'
  const Heading: 'h2' | 'h3' = `h${titleLevel}`

  return (
    <List
      className={cn(
        styles['info-panel-list'],
        styles[`info-panel-list-${variant}`],
        styles[`info-panel-list-${surface}`],
        styles[`info-panel-list-${size}`]
      )}
    >
      {variant === InfoPanelVariant.UNORDERED
        ? panels.map((panel, index) => (
            <InfoPanelItem
              key={panel.title}
              variant={InfoPanelVariant.UNORDERED}
              panel={panel}
              index={index}
              Heading={Heading}
            />
          ))
        : panels.map((panel, index) => (
            <InfoPanelItem
              key={panel.title}
              variant={InfoPanelVariant.ORDERED}
              panel={panel}
              index={index}
              Heading={Heading}
            />
          ))}
    </List>
  )
}
