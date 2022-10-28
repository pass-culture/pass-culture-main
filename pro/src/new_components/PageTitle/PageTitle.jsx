import PropTypes from 'prop-types'
import { useEffect } from 'react'

import { DEFAULT_PAGE_TITLE } from './_constants'

const PageTitle = ({ title }) => {
  useEffect(() => {
    document.title = `${title} - ${DEFAULT_PAGE_TITLE}`

    return () => {
      document.title = DEFAULT_PAGE_TITLE
    }
  }, [title])

  return null
}

PageTitle.propTypes = {
  title: PropTypes.string.isRequired,
}

export default PageTitle
