import classnames from 'classnames'
import React from 'react'

import MenuButton from '../client/MenuButton'

const PageWrapper = props => {
  const { Tag, name, redBg, noPadding, menuButton, children } = props
  const header = [].concat(children).find(e => e.type === 'header')
  const footer = [].concat(children).find(e => e.type === 'footer')
  const content = []
    .concat(children)
    .filter(e => e.type !== 'header' && e.type !== 'footer')
  return (
    <Tag
      className={classnames({
        page: true,
        [`${name}-page`]: true,
        'with-header': Boolean(header),
        'with-footer': Boolean(footer) || Boolean(menuButton),
        'red-bg': redBg,
        'no-padding': noPadding,
      })}
    >
      {header}
      <div className="page-content">{content}</div>
      {footer || (menuButton && <MenuButton {...menuButton} />)}
    </Tag>
  )
}

PageWrapper.defaultProps = {
  Tag: 'main',
}

export default PageWrapper
