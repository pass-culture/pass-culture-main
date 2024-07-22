import cn from 'classnames'
import React, { ReactNode, useId } from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import fullDownIcon from 'icons/full-down.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AccesLibreCollapse.module.scss'

export interface AccesLibreCollapseProps {
  title: string
  isAccessible: boolean
  icon: string
  children: ReactNode
}

export const AccesLibreCollapse = ({
  title,
  isAccessible,
  icon,
  children,
}: AccesLibreCollapseProps) => {
  const [isOpen, setIsOpen] = React.useState(true)
  const contentId = useId()

  const toggleCollapse = () => {
    setIsOpen(!isOpen)
  }

  return (
    <section className={styles['section']}>
      <header className={styles['header']}>
        <div className={styles['main-icon-container']}>
          <SvgIcon
            className={styles['main-icon']}
            src={icon}
            alt=""
            width="40"
          />
          <SvgIcon
            className={cn(
              styles['accessibility-icon'],
              isAccessible ? styles['accessible'] : styles['non-accessible']
            )}
            src={isAccessible ? fullValidateIcon : fullClearIcon}
            alt=""
            width="16"
          />
        </div>

        <div className={styles['title-container']}>
          <h3 className={styles['title']}>{title}</h3>
          <div className={styles['accessibility-label']}>
            {isAccessible ? 'Accessible' : 'Non accessible'}
          </div>
        </div>

        <button
          className={styles['collapse-button']}
          onClick={toggleCollapse}
          aria-label={`Voir les détails pour ${title}`}
          aria-expanded={isOpen}
          aria-controls={contentId}
        >
          <SvgIcon
            className={cn(styles['collapse-icon'], {
              [styles['open'] ?? '']: isOpen,
            })}
            src={fullDownIcon}
            alt=""
            width="24"
          />
        </button>
      </header>

      <div
        className={cn(styles['content'], { [styles['open'] ?? '']: isOpen })}
        id={contentId}
      >
        {isOpen && children}
      </div>
    </section>
  )
}
