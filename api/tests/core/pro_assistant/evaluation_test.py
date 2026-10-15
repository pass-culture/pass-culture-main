from pcapi.core.pro_assistant import evaluation
from pcapi.core.pro_assistant import portal_map


class EvaluationTest:
    def test_cases_are_valid(self):
        cases = evaluation.load_cases()

        assert len({case.id for case in cases}) == len(cases)
        for case in cases:
            assert set(case.expected_route_ids) <= set(portal_map.ROUTE_IDS), case.id
            assert not (case.out_of_scope and case.expected_route_ids), case.id

    def test_run_with_testing_backend(self):
        cases = [case for case in evaluation.load_cases() if case.id in ("create-individual-offer", "off-topic-code")]

        results = [evaluation.run_case(case) for case in cases]
        report = evaluation.format_report(results)

        # The testing backend always answers with the individual offer creation page
        assert results[0].route_ok is True
        assert results[0].scope_ok is True
        assert results[1].scope_ok is False
        assert "Routage : 1/1 bonnes pages proposées" in report
        assert "Périmètre : 1/2" in report

    def test_personal_data_is_not_sent(self):
        case = next(case for case in evaluation.load_cases() if case.id == "personal-data-pasted")

        result = evaluation.run_case(case)

        assert result.leaked_strings == []
