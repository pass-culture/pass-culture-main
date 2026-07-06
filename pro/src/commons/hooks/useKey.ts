import { useState } from 'react'

export const useKey = () => {
  const [value, setValue] = useState(0)

  const update = () => {
    setValue((previousValue) => previousValue + 1)
  }

  return {
    update,
    value,
  }
}
