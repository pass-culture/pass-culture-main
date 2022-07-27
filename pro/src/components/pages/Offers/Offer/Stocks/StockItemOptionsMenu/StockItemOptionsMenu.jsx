import '@reach/menu-button/styles.css'

import { Menu, MenuButton, MenuItem, MenuList } from '@reach/menu-button'
import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { ReactComponent as OptionMenuIcon } from 'icons/ico-more-horiz.svg'

import { ReactComponent as AddActivationCodeIcon } from '../assets/add-activation-code-light.svg'

import { ReactComponent as DeleteStockLightIcon } from './assets/delete-stock-light.svg'

const StockItemOptionsMenu = ({
  canAddActivationCodes,
  deleteButtonTitle,
  deleteStock,
  disableDeleteButton,
  hasActivationCodes,
  isNewStock,
  isOfferDisabled,
  setIsActivationCodesDialogOpen,
}) => {
  const openActivationCodesDialog = useCallback(
    () => setIsActivationCodesDialogOpen(true),
    [setIsActivationCodesDialogOpen]
  )

  return (
    <Menu className="stock-options-menu-container">
      <MenuButton
        className="stock-options-menu-button"
        disabled={isOfferDisabled}
        title="Opérations sur le stock"
        type="button"
      >
        <OptionMenuIcon
          alt="Opérations sur le stock"
          className="stock-options-menu-button-icon"
        />
      </MenuButton>
      <MenuList className="stock-options-menu-list">
        <MenuItem
          className="stock-options-menu-item"
          disabled={disableDeleteButton}
          onSelect={deleteStock}
          title={deleteButtonTitle}
        >
          <DeleteStockLightIcon
            alt="Supprimer le stock"
            aria-hidden
            className="stock-options-menu-item-icon"
          />
          <span className="stock-options-menu-item-text">
            Supprimer le stock
          </span>
        </MenuItem>
        {canAddActivationCodes && (
          <MenuItem
            className="stock-options-menu-item"
            disabled={!isNewStock || hasActivationCodes}
            onSelect={openActivationCodesDialog}
            title={
              isNewStock
                ? "Ajouter des codes d'activation"
                : "Les stocks déjà existants ne peuvent pas recevoir de codes d'activation"
            }
          >
            <AddActivationCodeIcon
              alt="Ajouter des codes d'activation"
              aria-hidden
              className="stock-options-menu-item-icon"
            />
            <span className="stock-options-menu-item-text">
              Ajouter des codes d’activation
            </span>
          </MenuItem>
        )}
      </MenuList>
    </Menu>
  )
}

StockItemOptionsMenu.propTypes = {
  canAddActivationCodes: PropTypes.bool.isRequired,
  deleteButtonTitle: PropTypes.string.isRequired,
  deleteStock: PropTypes.func.isRequired,
  disableDeleteButton: PropTypes.bool.isRequired,
  hasActivationCodes: PropTypes.bool.isRequired,
  isNewStock: PropTypes.bool.isRequired,
  isOfferDisabled: PropTypes.bool.isRequired,
  setIsActivationCodesDialogOpen: PropTypes.func.isRequired,
}

export default StockItemOptionsMenu
