import { useField } from 'formik'

import strokeBarcode from 'icons/stroke-barcode.svg'
import { Button } from 'ui-kit/Button/Button'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './DetailsEanSearch.module.scss'

type DetailsEanSearchProps = {
  isDisabled?: boolean
}

export const DetailsEanSearch = ({
  isDisabled = false,
}: DetailsEanSearchProps): JSX.Element => {
  const [, meta] = useField({
    name: 'ean',
    type: 'text',
  })

  const hasInputErrored = !!meta.error
  const label = (
    <>
      <Tag
        className={styles['details-ean-search-tag']}
        variant={TagVariant.BLUE}
      >
        Nouveau
      </Tag>
      <span>Scanner ou rechercher un produit par EAN</span>
    </>
  )

  return (
    <div className={styles['details-ean-search']}>
      <>
        <TextInput
          classNameLabel={styles['details-ean-search-label']}
          label={label}
          description="Format : EAN à 13 chiffres"
          name="ean"
          type="text"
          disabled={isDisabled}
          maxLength={13}
          isOptional
          countCharacters
          rightIcon={strokeBarcode}
          {...(isDisabled
            ? {
                clearButtonProps: {
                  tooltip: 'Effacer',
                  onClick: () => console.log('clear'),
                },
              }
            : {})}
        />
      </>
      <Button
        className={styles['details-ean-search-button']}
        disabled={isDisabled || hasInputErrored}
        onClick={() => console.log('search')}
      >
        Rechercher
      </Button>
    </div>
  )
}
