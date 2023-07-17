/* istanbul ignore file */
import React, { useState } from 'react'

import BaseInput from 'ui-kit/form/shared/BaseInput'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Title } from 'ui-kit/typography'

import styles from './Icons.module.scss'
import { fullIcons, otherIcons, shadowIcons, strokeIcons } from './iconsList'

const fuzzyMatch = (pattern: string, str: string) => {
  pattern = '.*' + pattern.toLowerCase().split('').join('.*') + '.*'
  const re = new RegExp(pattern)
  return re.test(str.toLowerCase())
}

const iconsSections = [
  { title: 'Full icons', icons: fullIcons },
  { title: 'Stroke icons', icons: strokeIcons },
  { title: 'Shadow icons', icons: shadowIcons },
  { title: 'Other icons', icons: otherIcons },
]

export const Icons = () => {
  const [searchInput, setSearchInput] = useState('')
  const [fillColorInput, setFillColorInput] = useState('#000000')
  const [backgroundColorInput, setBackgroundColorInput] = useState('#ffffff')

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
    <div className={styles['icon-stories']}>
      <div className={styles['search-input-container']}>
        <BaseInput
          name="search"
          onChange={event => setSearchInput(event.target.value)}
          placeholder="Rechercher ..."
          value={searchInput}
        />

        <BaseInput
          type="color"
          name="fillColor"
          onChange={event => setFillColorInput(event.target.value)}
          placeholder="#000000, red...."
          value={fillColorInput}
          className={styles['color-input']}
        />

        <BaseInput
          type="color"
          name="backgroundColor"
          onChange={event => setBackgroundColorInput(event.target.value)}
          placeholder="#000000, red...."
          value={backgroundColorInput}
          className={styles['color-input']}
        />
      </div>

      {iconsSections.map(section => {
        const filteredIcons = section.icons.filter(iconListItem =>
          fuzzyMatch(searchInput, iconListItem.src)
        )

        if (filteredIcons.length === 0) {
          return null
        }

        return (
          <div key={section.title}>
            <Title level={2}>{section.title}</Title>

            <div className={styles['icon-list']}>
              {filteredIcons.map(icon => {
                const fileNameParts = icon.src.split('/')
                const iconName = fileNameParts[fileNameParts.length - 1]
                  .split('.')[0]
                  .replace('full-', '')
                  .replace('stroke-', '')
                  .replace('shadow-', '')

                return (
                  <div
                    key={icon.src}
                    className={styles['container']}
                    onClick={onClick}
                    data-src={icon.src}
                  >
                    <div className={styles['copy-to-clipboard-wrapper']}>
                      <span className={styles['copy-to-clipboard-name']}>
                        Copié !
                      </span>
                    </div>

                    <div className={styles['icon-container']}>
                      <SvgIcon
                        src={icon.src}
                        alt={icon.src}
                        viewBox={icon.viewBox}
                        className={styles['icon']}
                        style={{
                          fill: fillColorInput,
                          color: fillColorInput,
                          backgroundColor: backgroundColorInput,
                        }}
                      />
                    </div>

                    <div className={styles['name-container']}>
                      <span className={styles['name']}>{iconName}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default {
  title: 'icons/Icons',
}
