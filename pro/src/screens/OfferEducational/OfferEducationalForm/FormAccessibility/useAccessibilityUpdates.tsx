import { useEffect, useState } from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import isEqual from 'lodash.isequal'
import { useFormikContext } from 'formik'

const useAccessibilityUpdates = (): void => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  const [prevValue, setPrevValue] = useState<
    IOfferEducationalFormValues['accessibility'] | null
  >(values.accessibility)

  useEffect(() => {
    if (!isEqual(values.accessibility, prevValue)) {
      const wasNone = prevValue?.none ?? false
      const isNone = values.accessibility.none

      const haveOneOrMoreAccessibility = [
        values.accessibility.visual,
        values.accessibility.audio,
        values.accessibility.motor,
        values.accessibility.mental,
      ].includes(true)

      if (!wasNone && isNone) {
        const newValue = {
          visual: false,
          audio: false,
          motor: false,
          mental: false,
          none: true,
        }
        setPrevValue(newValue)
        setFieldValue('accessibility', newValue)
      }

      if (wasNone && isNone && haveOneOrMoreAccessibility) {
        const newValue = {
          ...values.accessibility,
          none: false,
        }
        setPrevValue(newValue)
        setFieldValue('accessibility', newValue)
      }
    }
  }, [values.accessibility, setFieldValue, prevValue])
}

export default useAccessibilityUpdates
