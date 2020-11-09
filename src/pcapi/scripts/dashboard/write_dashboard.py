from functools import partial
from typing import Callable
from typing import List
from typing import Optional

from gspread import Spreadsheet
from pygsheets import Worksheet

from pcapi.connectors.google_spreadsheet import get_dashboard_spreadsheet
from pcapi.domain.departments import DEPARTEMENT_CODE_VISIBILITY
from pcapi.scripts.dashboard.diversification_statistics import (
    query_get_booking_counts_grouped_by_type_and_medium_for_departement,
)
from pcapi.scripts.dashboard.diversification_statistics import (
    query_get_offer_counts_grouped_by_type_and_medium_for_departement,
)
from pcapi.scripts.dashboard.diversification_statistics import count_all_cancelled_bookings
from pcapi.scripts.dashboard.diversification_statistics import get_all_bookings_count
from pcapi.scripts.dashboard.diversification_statistics import get_all_used_or_finished_bookings
from pcapi.scripts.dashboard.diversification_statistics import get_offer_counts_grouped_by_type_and_medium
from pcapi.scripts.dashboard.diversification_statistics import get_offerer_count
from pcapi.scripts.dashboard.diversification_statistics import get_offerer_with_stock_count
from pcapi.scripts.dashboard.diversification_statistics import get_offerers_with_non_cancelled_bookings_count
from pcapi.scripts.dashboard.diversification_statistics import get_offerers_with_offer_available_on_discovery_count
from pcapi.scripts.dashboard.diversification_statistics import get_offerers_with_offers_available_on_search_count
from pcapi.scripts.dashboard.diversification_statistics import get_offers_available_on_discovery_count
from pcapi.scripts.dashboard.diversification_statistics import get_offers_available_on_search_count
from pcapi.scripts.dashboard.diversification_statistics import get_offers_with_non_cancelled_bookings_count
from pcapi.scripts.dashboard.diversification_statistics import get_offers_with_user_offerer_and_stock_count
from pcapi.scripts.dashboard.diversification_statistics import query_get_booking_counts_grouped_by_type_and_medium
from pcapi.scripts.dashboard.diversification_statistics import query_get_offer_counts_grouped_by_type_and_medium
from pcapi.scripts.dashboard.finance_statistics import get_top_20_offerers_by_amount_table
from pcapi.scripts.dashboard.finance_statistics import get_top_20_offerers_table_by_number_of_bookings
from pcapi.scripts.dashboard.finance_statistics import get_top_20_offers_table
from pcapi.scripts.dashboard.finance_statistics import get_total_amount_spent
from pcapi.scripts.dashboard.finance_statistics import get_total_amount_to_pay
from pcapi.scripts.dashboard.finance_statistics import get_total_deposits
from pcapi.scripts.dashboard.users_statistics import count_activated_users
from pcapi.scripts.dashboard.users_statistics import count_users_having_booked
from pcapi.scripts.dashboard.users_statistics import get_mean_amount_spent_by_user
from pcapi.scripts.dashboard.users_statistics import get_mean_number_of_bookings_per_user_having_booked
from pcapi.scripts.dashboard.users_statistics import get_non_cancelled_bookings_by_user_departement


EXPERIMENTATION_DEPARTEMENTS = list(DEPARTEMENT_CODE_VISIBILITY.keys())


class DashboardConfig:
    space_between_lines = 1
    space_between_tables = 2
    space_between_sections = 3
    max_rows_for_departements_table = 100
    max_rows_for_category_and_digital_table = 50
    top_20_table_size = 21


def write_dashboard_worksheet(spreadsheet: Spreadsheet, tab_name: str):
    current_row = 1
    worksheet = _initialize_worksheet(spreadsheet, tab_name)
    worksheet.update_value(f'A{current_row}', 'TABLEAU DE BORD PASS CULTURE')
    current_row += DashboardConfig.space_between_sections
    departement_code = _get_departement_code(tab_name)
    current_row = _write_usage_section(departement_code, worksheet, current_row)
    current_row = _write_diversification_section(departement_code, worksheet, current_row)
    _write_finance_section(departement_code, worksheet, current_row)


def write_dashboard(connect_to_spreadsheet: Callable = get_dashboard_spreadsheet,
                    write_worksheet: Callable = write_dashboard_worksheet,
                    experimentation_departements: List = EXPERIMENTATION_DEPARTEMENTS):
    worksheet_names = experimentation_departements
    worksheet_names.append('Global')
    spreadsheet = connect_to_spreadsheet()
    for worksheet in worksheet_names:
        write_worksheet(spreadsheet, worksheet)


def _get_departement_code(tab_name: str) -> Optional[str]:
    departement_code = None
    if tab_name != 'Global':
        departement_code = tab_name
    return departement_code


def _write_finance_section(departement_code: str, worksheet: Worksheet, current_row: int):
    worksheet.update_value(f'A{current_row}', '3/ FINANCEMENT')
    current_row += DashboardConfig.space_between_tables
    current_row = _write_finance_table(departement_code, worksheet, current_row)
    current_row += DashboardConfig.space_between_tables
    worksheet.update_value(f'A{current_row}', 'TOP 20 OFFRES')
    current_row += DashboardConfig.space_between_tables
    worksheet.set_dataframe(get_top_20_offers_table(departement_code), f'A{current_row}')
    current_row += DashboardConfig.space_between_tables + DashboardConfig.top_20_table_size
    worksheet.update_value(f'A{current_row}', 'TOP 20 OFFREURS')
    current_row += DashboardConfig.space_between_tables
    worksheet.set_dataframe(get_top_20_offerers_table_by_number_of_bookings(departement_code), f'A{current_row}')
    current_row += DashboardConfig.space_between_tables + DashboardConfig.top_20_table_size
    worksheet.set_dataframe(get_top_20_offerers_by_amount_table(departement_code), f'A{current_row}')


def _write_diversification_section(departement_code: str, worksheet: Worksheet, current_row: int) -> int:
    worksheet.update_value(f'A{current_row}', '2/ DIVERSIFICATION')
    current_row += DashboardConfig.space_between_tables
    current_row = _write_diversification_table(departement_code, worksheet, current_row)
    current_row += DashboardConfig.space_between_tables
    _write_offer_counts_grouped_by_type_and_medium(departement_code, worksheet, current_row)
    _write_bookings_by_type_and_digital_counts(departement_code, worksheet, current_row)
    current_row += DashboardConfig.space_between_sections + DashboardConfig.max_rows_for_category_and_digital_table
    return current_row


def _write_usage_section(departement_code: str, worksheet: Worksheet, current_row: int) -> int:
    worksheet.update_value(f'A{current_row}', '1/ UTILISATION')
    current_row += DashboardConfig.space_between_tables
    current_row = _write_usage_table(departement_code, worksheet, current_row, )
    current_row += DashboardConfig.space_between_tables
    if not departement_code:
        worksheet.set_dataframe(get_non_cancelled_bookings_by_user_departement(), f'A{current_row}')
        current_row += DashboardConfig.max_rows_for_departements_table
    current_row += DashboardConfig.space_between_sections
    return current_row


def _initialize_worksheet(spreadsheet: Spreadsheet, tab_name: str) -> Worksheet:
    all_worksheets = [ws.title for ws in spreadsheet.worksheets()]
    if tab_name in all_worksheets:
        worksheet = spreadsheet.worksheet_by_title(tab_name)
        worksheet.clear()
    else:
        spreadsheet.add_worksheet(tab_name, rows=300)
        worksheet = spreadsheet.worksheet_by_title(tab_name)
    return worksheet


def _write_bookings_by_type_and_digital_counts(departement_code: str, worksheet: Worksheet, current_row: int):
    if departement_code:
        bookings_by_type_and_digital_counts = get_offer_counts_grouped_by_type_and_medium(
            partial(query_get_booking_counts_grouped_by_type_and_medium_for_departement,
                    departement_code=departement_code), 'Nombre de réservations')
    else:
        bookings_by_type_and_digital_counts = get_offer_counts_grouped_by_type_and_medium(
            query_get_booking_counts_grouped_by_type_and_medium, 'Nombre de réservations')
    worksheet.set_dataframe(bookings_by_type_and_digital_counts, f'E{current_row}')


def _write_offer_counts_grouped_by_type_and_medium(departement_code: str, worksheet: Worksheet, current_row: int):
    if departement_code:
        offer_counts_grouped_by_type_and_medium = get_offer_counts_grouped_by_type_and_medium(
            partial(query_get_offer_counts_grouped_by_type_and_medium_for_departement,
                    departement_code=departement_code),
            'Nombre d\'offres')
    else:
        offer_counts_grouped_by_type_and_medium = get_offer_counts_grouped_by_type_and_medium(
            query_get_offer_counts_grouped_by_type_and_medium,
            'Nombre d\'offres')
    worksheet.set_dataframe(offer_counts_grouped_by_type_and_medium, f'A{current_row}')


def _write_finance_table(departement_code: str, worksheet: Worksheet, current_row: int) -> int:
    worksheet.update_value(f'A{current_row}', 'Indicateur')
    worksheet.update_value(f'B{current_row}', 'Valeur')
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Crédit total activé')
    worksheet.update_value(f'B{current_row}', get_total_deposits(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Crédit total dépensé')
    worksheet.update_value(f'B{current_row}', get_total_amount_spent(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Dépenses totales à rembourser')
    worksheet.update_value(f'B{current_row}', get_total_amount_to_pay(departement_code))
    return current_row


def _write_diversification_table(departement_code: str, worksheet: Worksheet, current_row: int) -> int:
    worksheet.update_value(f'A{current_row}', 'Indicateur')
    worksheet.update_value(f'B{current_row}', 'Valeur')
    worksheet.update_value(f'E{current_row}', 'Indicateur')
    worksheet.update_value(f'F{current_row}', 'Valeur')
    worksheet.update_value(f'I{current_row}', 'Indicateur')
    worksheet.update_value(f'J{current_row}', 'Valeur')
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs depuis le début du pass')
    worksheet.update_value(f'B{current_row}', get_offerer_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres depuis le début du pass')
    worksheet.update_value(f'F{current_row}', get_offers_with_user_offerer_and_stock_count(departement_code))
    worksheet.update_value(f'I{current_row}', '# Réservations')
    worksheet.update_value(f'J{current_row}', get_all_bookings_count(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs ayant mis une offre depuis le début du pass')
    worksheet.update_value(f'B{current_row}', get_offerer_with_stock_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres disponibles')
    worksheet.update_value(f'F{current_row}', get_offers_available_on_search_count(departement_code))
    worksheet.update_value(f'I{current_row}', '# Réservations validées')
    worksheet.update_value(f'J{current_row}', get_all_used_or_finished_bookings(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs ayant une offre disponible')
    worksheet.update_value(f'B{current_row}', get_offerers_with_offers_available_on_search_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres mises en avant')
    worksheet.update_value(f'F{current_row}', get_offers_available_on_discovery_count(departement_code))
    worksheet.update_value(f'I{current_row}', '# Réservations annulées')
    worksheet.update_value(f'J{current_row}', count_all_cancelled_bookings(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs ayant une offre mise en avant')
    worksheet.update_value(f'B{current_row}', get_offerers_with_offer_available_on_discovery_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres réservées')
    worksheet.update_value(f'F{current_row}', get_offers_with_non_cancelled_bookings_count(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs réservés')
    worksheet.update_value(f'B{current_row}', get_offerers_with_non_cancelled_bookings_count(departement_code))
    return current_row


def _write_usage_table(departement_code: str, worksheet: Worksheet, current_row: int) -> int:
    worksheet.update_value(f'A{current_row}', '# Comptes activés')
    worksheet.update_value(f'B{current_row}', count_activated_users(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Comptes ayant réservé')
    worksheet.update_value(f'B{current_row}', count_users_having_booked(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '# Moyen de réservations')
    worksheet.update_value(f'B{current_row}', get_mean_number_of_bookings_per_user_having_booked(departement_code))
    current_row += DashboardConfig.space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Moyen de dépenses')
    worksheet.update_value(f'B{current_row}', get_mean_amount_spent_by_user(departement_code))
    return current_row
