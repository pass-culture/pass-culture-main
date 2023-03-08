import { useEffect } from 'react'

const DEFAULT_PAGE_TITLE = 'pass Culture Pro'

interface Props {
  title: string
}

const PageTitle = ({ title }: Props) => {
  useEffect(() => {
    document.title = `${title} - ${DEFAULT_PAGE_TITLE}`

    return () => {
      document.title = DEFAULT_PAGE_TITLE
    }
  }, [title])

  return null
}

export default PageTitle
