import React from 'react'

import {
  departmentLabelByValue,
  MAINLAND_OPTION_VALUE,
  domtomOptions,
  departmentOptions,
} from 'app/constants/departmentOptions'

export const getInterventionAreaLabels = (
  interventionArea: string[]
): string => {
  const labels: string[] = []

  if (interventionArea.includes(MAINLAND_OPTION_VALUE)) {
    labels.push(departmentLabelByValue[MAINLAND_OPTION_VALUE])

    domtomOptions.forEach(domtomOption => {
      if (interventionArea.includes(domtomOption.value.toString())) {
        const [departmentCode, departmentLabel] =
          domtomOption.label.split(' - ')
        labels.push(`${departmentLabel} (${departmentCode})`)
      }
    })

    return labels.join(' - ')
  }

  departmentOptions.forEach(interventionOption => {
    if (interventionArea.includes(interventionOption.value.toString())) {
      const [departmentCode, departmentLabel] =
        interventionOption.label.split(' - ')
      labels.push(`${departmentLabel} (${departmentCode})`)
    }
  })

  return labels.join(' - ')
}

const OfferInterventionArea = ({
  interventionArea,
}: {
  interventionArea: string[]
}): JSX.Element => <div>{getInterventionAreaLabels(interventionArea)}</div>

export default OfferInterventionArea
