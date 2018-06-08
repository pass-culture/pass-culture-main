import classnames from 'classnames'
import React from 'react'

import BackButton from './BackButton'
import Header from './Header'

const PageWrapper = props => {
  const {
    header,
    Tag,
    name,
    redBg,
    noContainer,
    noHeader,
    noPadding,
    backButton,
    children,
    loading,
    notification,
  } = props
  const footer = [].concat(children).find(e => e && e.type === 'footer')
  const content = []
    .concat(children)
    .filter(e => e && e.type !== 'header' && e.type !== 'footer')
  return [
    !noHeader && <Header key='header' {...header} />,
    <Tag
      className={classnames({
        page: true,
        [`${name}-page`]: true,
        'with-header': Boolean(header),
        'with-footer': Boolean(footer),
        'red-bg': redBg,
        'no-padding': noPadding,
        container: !noContainer,
        loading,
      })}
      key='page-wrapper'
    >
      <div className={classnames('page-content')}>
        {notification && (
          <div className={`notification is-${notification.type || 'info'}`}>
            <button className="delete">Ok</button>
            {notification.text}
          </div>
        )}
        {content}
      </div>
      {footer}
    </Tag>
  ]
}

PageWrapper.defaultProps = {
  Tag: 'main',
}

export default PageWrapper
