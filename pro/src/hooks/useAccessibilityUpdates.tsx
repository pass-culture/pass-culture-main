import isEqual from 'lodash.isequal'
import { useEffect, useState } from 'react'

import { IAccessibiltyFormValues } from 'core/shared'

const useAccessibilityUpdates = (
  values: IAccessibiltyFormValues,
  handleChange: (values: IAccessibiltyFormValues) => void
): void => {
  const [prevValue, setPrevValue] = useState<IAccessibiltyFormValues>(values)

  useEffect(() => {
    if (!isEqual(values, prevValue)) {
      const wasNone = prevValue?.none ?? false
      const isNone = values.none
      let newValues = { ...values }

      if (!wasNone && isNone) {
        newValues = {
          ...newValues,
          visual: false,
          audio: false,
          mental: false,
          motor: false,
        }
      }

      const haveOneOrMoreAccessibility = [
        values.visual,
        values.audio,
        values.motor,
        values.mental,
      ].includes(true)
      if (wasNone && isNone && haveOneOrMoreAccessibility) {
        newValues = {
          ...newValues,
          none: false,
        }
      }

      if (!isEqual(values, newValues)) {
        handleChange(newValues)
      }

      setPrevValue(newValues)
    }
  }, [values, handleChange, prevValue])
}

export default useAccessibilityUpdates
