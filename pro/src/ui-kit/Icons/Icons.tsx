/* istanbul ignore file */
import cn from 'classnames'
import React, { useState } from 'react'

import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import BaseInput from 'ui-kit/form/shared/BaseInput'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Title } from 'ui-kit/typography'

import styles from './Icons.module.scss'

function fuzzyMatch(pattern: string, str: string) {
  pattern = '.*' + pattern.toLowerCase().split('').join('.*') + '.*'
  const re = new RegExp(pattern)
  return re.test(str.toLowerCase())
}

interface IconListItem {
  src: string
  viewbox?: string
}

const iconList = [{ src: 'icons/user.svg' }]

export const Icons = () => {
  const [filteredIcons, setFilteredIcons] = useState<IconListItem[]>(iconList)
  const [whiteIcon, setWhiteIcon] = useState<boolean>(false)
  const [blackBackground, setBlackBackground] = useState<boolean>(false)

  const handleSearchOnChange: React.ChangeEventHandler<
    HTMLInputElement
  > = e => {
    e.stopPropagation()
    const search = e.target.value
    const newFilteredIcons = iconList.filter(iconListItem =>
      fuzzyMatch(search, iconListItem.src)
    )
    setFilteredIcons(newFilteredIcons)
  }

  const onClickToggleIconColor = () => {
    setWhiteIcon(current => !current)
  }
  const onClickToggleBackgroundColor = () => {
    setBlackBackground(current => !current)
  }
  const onClick: React.MouseEventHandler<HTMLDivElement> = e => {
    e.persist()
    const target = e.currentTarget as Element

    navigator.clipboard.writeText(target.getAttribute('data-src') ?? '')

    target.classList.add(styles['copy-to-clipboard'])
    const timeoutId = setTimeout(() => {
      target.classList.remove(styles['copy-to-clipboard'])
      clearTimeout(timeoutId)
    }, 600)
  }

  return (
    <div
      className={cn(styles['icon-stories'], {
        [styles['icon-white']]: whiteIcon,
        [styles['background-black']]: blackBackground,
      })}
    >
      <div className={styles['options']}>
        <p>
          Les couleurs des icons sont normalisé en noir (via la propriété css (
          <code> fill </code>)
        </p>
        <div className={styles['button-group']}>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={onClickToggleIconColor}
          >
            {whiteIcon
              ? 'Afficher les icons en noir'
              : 'Afficher les icons en blanc'}
          </Button>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={onClickToggleBackgroundColor}
          >
            {blackBackground
              ? 'Afficher les background en blanc'
              : 'Afficher les background en noir'}
          </Button>
        </div>
      </div>

      <Title level={1}>Liste des icones</Title>

      <div className={styles['search-input-container']}>
        <BaseInput
          className={styles['search-input']}
          name="search"
          onChange={handleSearchOnChange}
          placeholder="Rechercher ..."
        />
      </div>

      <div className={styles['icon-list']}>
        {filteredIcons.map(icon => (
          <div
            key={icon.src}
            className={styles['container']}
            onClick={onClick}
            data-src={icon.src}
          >
            <div className={styles['copy-to-clipboard-wrapper']}>
              <span className={styles['copy-to-clipboard-name']}>Copié !</span>
            </div>
            <div className={styles['icon-container']}>
              <SvgIcon
                src={icon.src}
                alt={icon.src}
                viewBox={icon.viewbox}
                className={styles['icon']}
              />
            </div>
            <div className={styles['name-container']}>
              <span className={styles['name']}>{icon.src}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
