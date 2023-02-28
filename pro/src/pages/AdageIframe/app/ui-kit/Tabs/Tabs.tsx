import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'

import './Tabs.scss'

interface ITab {
  label: string
  key: string
  Icon?: FunctionComponent<SVGProps<SVGSVGElement>>
  onClick: () => void
}

interface IFilterTabsProps {
  tabs: ITab[]
  selectedKey?: string
}

const Tabs = ({ selectedKey, tabs }: IFilterTabsProps): JSX.Element => (
  <ul className="tabs">
    {tabs.map(({ key, label, Icon, onClick }) => {
      return (
        <li
          className={cn('tabs-tab', {
            ['is-selected']: selectedKey === key,
          })}
          key={key}
        >
          <button className="tabs-tab-button" onClick={onClick} type="button">
            {Icon && <Icon className="tabs-tab-icon" />}
            <span>{label}</span>
          </button>
        </li>
      )
    })}
  </ul>
)

export default Tabs
