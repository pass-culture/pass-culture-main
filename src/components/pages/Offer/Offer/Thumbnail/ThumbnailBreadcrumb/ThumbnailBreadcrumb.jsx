import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB } from 'components/layout/Breadcrumb'

const ThumbnailBreadcrumb = () => {
  const activeStep = 'import'
  const steps = [
    {
      id: 'import',
      label: 'Importer',
      url: '/',
    },
    {
      id: 'use_a_url',
      label: 'Utiliser une URL',
      url: '/',
    },
  ]

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={steps}
      styleType={STYLE_TYPE_TAB}
    />
  )
}

export default ThumbnailBreadcrumb
