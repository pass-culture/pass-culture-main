import React from 'react'

const renderPageHeader = searchPageTitle => (
  <header className="no-dotted-border">
    <h1 className="is-normal fs19">
      {searchPageTitle}
    </h1>
  </header>
)

export default renderPageHeader
