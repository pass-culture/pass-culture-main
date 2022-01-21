import { useCallback, useState } from 'react'

type UseModal = (defaultVisibility?: boolean) => {
  visible: boolean
  showModal: () => void
  hideModal: () => void
  toggleModal: () => void
}

export const useModal: UseModal = (defaultVisibility = false) => {
  const [visible, setVisible] = useState(defaultVisibility)

  const showModal = useCallback(() => setVisible(true), [])
  const hideModal = useCallback(() => setVisible(false), [])
  const toggleModal = useCallback(() => setVisible(visible => !visible), [])

  return { visible, showModal, hideModal, toggleModal }
}
