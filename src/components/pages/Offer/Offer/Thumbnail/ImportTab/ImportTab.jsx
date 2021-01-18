import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB } from 'components/layout/Breadcrumb'
import { IMPORT_TAB_ID, URL_TAB_ID } from 'components/pages/Offer/Offer/Thumbnail/_constants'

const ImportTab = ({ activeTab, changeTab }) => {
  const steps = [
    {
      id: IMPORT_TAB_ID,
      label: 'Importer',
      onClick: changeTab(IMPORT_TAB_ID),
      url: '#',
    },
    {
      id: URL_TAB_ID,
      label: 'Utiliser une URL',
      onClick: changeTab(URL_TAB_ID),
      url: '#',
    },
  ]

  return (
    <Breadcrumb
      activeStep={activeTab}
      steps={steps}
      styleType={STYLE_TYPE_TAB}
    />
  )
}

ImportTab.propTypes = {
  activeTab: PropTypes.string.isRequired,
  changeTab: PropTypes.func.isRequired,
}

export default ImportTab
