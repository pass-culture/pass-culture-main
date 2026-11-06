import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { type FormatEnum, NatureEnum } from '@/apiClient/v1'
import { GET_NFD_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setFormat, setNature } from '@/commons/store/nfd/reducer'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import strokeBookIcon from '@/icons/stroke-book.svg'
import strokeCardsIcon from '@/icons/stroke-cards.svg'
import strokeEventsIcon from '@/icons/stroke-events.svg'
import strokeNumIcon from '@/icons/stroke-num.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './IndividualOfferV2NatureFormatDomain.module.scss'

const natureIcon: Record<NatureEnum, string> = {
  [NatureEnum.BIEN]: strokeBookIcon,
  [NatureEnum.CARTE_ABONNEMENT]: strokeCardsIcon,
  [NatureEnum.EVENEMENT]: strokeEventsIcon,
  [NatureEnum.NUMERIQUE]: strokeNumIcon,
}

const IndividualOfferV2NatureFormatDomain = (): JSX.Element => {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const nfdQuery = useSWR([GET_NFD_QUERY_KEY], () =>
    api.getNatureFormatDomain()
  )
  const { nature: selectedNature, format: selectedFormat } = useAppSelector(
    (state) => state.nfd
  )

  const onSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault()
    await navigate('/offre/individuelle/v2/creation/description')
  }

  if (!nfdQuery.data) {
    return <Spinner />
  }

  const natures = nfdQuery.data
  return (
    <form onSubmit={onSubmit}>
      <FormLayout>
        <FormLayout.Section title="Nature et format">
          <FormLayout.Row lgSpaceAfter>
            <RadioButtonGroup
              name="nature"
              label="Sélectionnez la nature"
              variant={'detailed'}
              checkedOption={selectedNature as string}
              display="horizontal"
              sizing="hug"
              onChange={(event) =>
                dispatch(setNature(event.target.value as NatureEnum))
              }
              options={natures.map((nature) => ({
                label: nature.label,
                value: nature.name,
                asset: {
                  variant: 'icon',
                  src: natureIcon[nature.name],
                },
              }))}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            {selectedNature && (
              <div className={styles['format']}>
                <RadioButtonGroup
                  name="format"
                  label="Sélectionnez le format"
                  variant={'detailed'}
                  checkedOption={selectedFormat as string}
                  display="horizontal"
                  sizing="hug"
                  onChange={(event) =>
                    dispatch(setFormat(event.target.value as FormatEnum))
                  }
                  options={
                    natures
                      .find((nature) => nature.name === selectedNature)
                      ?.formats.map((format) => ({
                        sizing: 'hug',
                        label: format.label,
                        value: format.format,
                      })) ?? []
                  }
                />
              </div>
            )}
          </FormLayout.Row>
        </FormLayout.Section>
      </FormLayout>
      <ActionsBarSticky hasSideNav={false} isEmbedded={true}>
        <ActionsBarSticky.Left>
          <Button
            as="router-link"
            to="/accueil"
            color={ButtonColor.NEUTRAL}
            variant={ButtonVariant.SECONDARY}
            label="Annuler et quitter"
          />
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <Button
            type="submit"
            color={ButtonColor.BRAND}
            variant={ButtonVariant.PRIMARY}
            label="Étape suivante"
            icon={strokeRightIcon}
            disabled={!selectedFormat || !selectedNature}
            iconPosition={IconPositionEnum.RIGHT}
          />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </form>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2NatureFormatDomain
