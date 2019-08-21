from connectors.google_spreadsheet import get_dashboard_worksheet
from scripts.dashboard import count_activated_users, count_users_having_booked, \
    get_mean_number_of_bookings_per_user_having_booked, get_mean_amount_spent_by_user, \
    get_non_cancelled_bookings_by_user_departement, get_offerer_count, get_offers_with_user_offerer_and_stock_count, \
    get_all_bookings_count, get_offerer_with_stock_count, get_offers_available_on_discovery_count, \
    get_all_used_or_finished_bookings, get_offerers_with_offer_available_on_discovery_count, \
    get_offers_with_non_cancelled_bookings_count, get_offerers_with_non_cancelled_bookings_count, get_total_deposits, \
    get_total_amount_spent, get_total_amount_to_pay, get_top_20_offers_table, \
    get_top_20_offerers_table_by_number_of_bookings, get_top_20_offerers_by_amount_table
from scripts.dashboard.diversification_statistics import get_offer_counts_grouped_by_type_and_medium, \
    query_get_offer_counts_grouped_by_type_and_medium, query_get_booking_counts_grouped_by_type_and_medium, \
    count_all_cancelled_bookings


def write_dashboard(tab_name: str):
    current_row = 1
    space_between_lines = 1
    space_between_tables = 2
    space_between_sections = 3
    max_rows_for_departements_table = 100
    max_rows_for_category_and_digital_table = 50
    top_20_table_size = 21

    spreadsheet = get_dashboard_worksheet()
    all_worksheets = [ws.title for ws in spreadsheet.worksheets()]
    if tab_name not in all_worksheets:
        spreadsheet.add_worksheet(tab_name)

    departement_code = None
    if tab_name != 'Global':
        departement_code = tab_name

    worksheet = spreadsheet.worksheet_by_title(tab_name)

    worksheet.clear()

    worksheet.update_value(f'A{current_row}', 'TABLEAU DE BORD PASS CULTURE')

    current_row += space_between_sections

    worksheet.update_value(f'A{current_row}', '1/ UTILISATION')
    current_row += space_between_tables
    current_row = _write_usage_table(departement_code, worksheet, current_row, space_between_lines)
    current_row += space_between_tables
    if not departement_code:
        worksheet.set_dataframe(get_non_cancelled_bookings_by_user_departement(), f'A{current_row}')
        current_row += max_rows_for_departements_table
    current_row += space_between_sections

    worksheet.update_value(f'A{current_row}', '2/ DIVERSIFICATION')
    current_row += space_between_tables
    current_row = _write_diversification_table(departement_code, worksheet, current_row, space_between_lines)
    current_row += space_between_tables
    offer_counts_grouped_by_type_and_medium = get_offer_counts_grouped_by_type_and_medium(
        query_get_offer_counts_grouped_by_type_and_medium,
        'Nombre d\'offres')
    worksheet.set_dataframe(offer_counts_grouped_by_type_and_medium, f'A{current_row}')
    bookings_by_type_and_digital_counts = get_offer_counts_grouped_by_type_and_medium(
        query_get_booking_counts_grouped_by_type_and_medium, 'Nombre de réservations')
    worksheet.set_dataframe(bookings_by_type_and_digital_counts, f'E{current_row}')
    current_row += space_between_sections + max_rows_for_category_and_digital_table

    worksheet.update_value(f'A{current_row}', '3/ FINANCEMENT')
    current_row += space_between_tables
    current_row = _write_finance_table(departement_code, worksheet, current_row, space_between_lines)
    current_row += space_between_tables
    worksheet.update_value(f'A{current_row}', 'TOP 20 OFFRES')
    current_row += space_between_tables
    worksheet.set_dataframe(get_top_20_offers_table(departement_code), f'A{current_row}')
    current_row += space_between_tables + top_20_table_size
    worksheet.update_value(f'A{current_row}', 'TOP 20 OFFREURS')
    current_row += space_between_tables
    worksheet.set_dataframe(get_top_20_offerers_table_by_number_of_bookings(departement_code), f'A{current_row}')
    current_row += space_between_tables + top_20_table_size
    worksheet.set_dataframe(get_top_20_offerers_by_amount_table(departement_code), f'A{current_row}')


def _write_finance_table(departement_code, worksheet, current_row, space_between_lines):
    worksheet.update_value(f'A{current_row}', 'Indicateur')
    worksheet.update_value(f'B{current_row}', 'Valeur')
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Crédit total activé')
    worksheet.update_value(f'B{current_row}', get_total_deposits(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Crédit total dépensé')
    worksheet.update_value(f'B{current_row}', get_total_amount_spent(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Dépenses totales à rembourser')
    worksheet.update_value(f'B{current_row}', get_total_amount_to_pay(departement_code))
    return current_row


def _write_diversification_table(departement_code, worksheet, current_row, space_between_lines):
    worksheet.update_value(f'A{current_row}', 'Indicateur')
    worksheet.update_value(f'B{current_row}', 'Valeur')
    worksheet.update_value(f'E{current_row}', 'Indicateur')
    worksheet.update_value(f'F{current_row}', 'Valeur')
    worksheet.update_value(f'I{current_row}', 'Indicateur')
    worksheet.update_value(f'J{current_row}', 'Valeur')
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs depuis le début du pass')
    worksheet.update_value(f'B{current_row}', get_offerer_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres depuis le début du pass')
    worksheet.update_value(f'F{current_row}', get_offers_with_user_offerer_and_stock_count(departement_code))
    worksheet.update_value(f'I{current_row}', '# Réservations')
    worksheet.update_value(f'J{current_row}', get_all_bookings_count(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs ayant mis une offre depuis le début du pass')
    worksheet.update_value(f'B{current_row}', get_offerer_with_stock_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres disponibles')
    worksheet.update_value(f'F{current_row}', get_offers_available_on_discovery_count(departement_code))
    worksheet.update_value(f'I{current_row}', '# Réservations validées')
    worksheet.update_value(f'J{current_row}', get_all_used_or_finished_bookings(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs ayant une offre disponible')
    worksheet.update_value(f'B{current_row}', get_offerers_with_offer_available_on_discovery_count(departement_code))
    worksheet.update_value(f'E{current_row}', '# Offres réservées')
    worksheet.update_value(f'F{current_row}', get_offers_with_non_cancelled_bookings_count(departement_code))
    worksheet.update_value(f'I{current_row}', '# Réservations annulées')
    worksheet.update_value(f'J{current_row}', count_all_cancelled_bookings(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '# Offreurs réservés')
    worksheet.update_value(f'B{current_row}', get_offerers_with_non_cancelled_bookings_count(departement_code))
    return current_row


def _write_usage_table(departement_code, worksheet, current_row, space_between_lines):
    worksheet.update_value(f'A{current_row}', '# Comptes activés')
    worksheet.update_value(f'B{current_row}', count_activated_users(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '# Comptes ayant réservé')
    worksheet.update_value(f'B{current_row}', count_users_having_booked(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '# Moyen de réservations')
    worksheet.update_value(f'B{current_row}', get_mean_number_of_bookings_per_user_having_booked(departement_code))
    current_row += space_between_lines
    worksheet.update_value(f'A{current_row}', '€ Moyen de dépenses')
    worksheet.update_value(f'B{current_row}', get_mean_amount_spent_by_user(departement_code))
    return current_row