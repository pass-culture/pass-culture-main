import argparse
import copy

from pcapi.app import app
from pcapi.core.fraud import models as fraud_models
from pcapi.models import db


def process(min_id: int, max_id: int) -> None:
    print(f"Processing {min_id}-{max_id}")

    fraud_checks_query = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        fraud_models.BeneficiaryFraudCheck.id.between(min_id, max_id),
        fraud_models.BeneficiaryFraudCheck.resultContent["instructor_annotation"].astext.is_not(None),
    ).order_by(fraud_models.BeneficiaryFraudCheck.id.desc())

    for fraud_check in fraud_checks_query:
        print(f'fraud check {fraud_check.id}: {fraud_check.resultContent["instructor_annotation"]}')
        instructor_annotation = fraud_check.resultContent["instructor_annotation"]
        if instructor_annotation:
            content = copy.deepcopy(fraud_check.resultContent)
            if isinstance(instructor_annotation, str):
                content["instructor_annotation"] = {"value": instructor_annotation}
                print("===(str)=========>", content["instructor_annotation"])
            elif isinstance(instructor_annotation, dict):
                value = instructor_annotation["value"]
                if value is None:
                    content["instructor_annotation"] = None
                    print("===(dict)========>", content["instructor_annotation"])
                elif isinstance(value, dict):
                    content["instructor_annotation"] = value
                    print("===(dict+dict)===>", content["instructor_annotation"])
                elif isinstance(value, str):
                    try:
                        fraud_models.DmsInstructorAnnotationEnum(value)
                    except ValueError:
                        match instructor_annotation["value"]:
                            case "SI" | "SM":
                                content["instructor_annotation"]["value"] = "S"
                            case "IDD" | "IDH" | "IDI" | "IDR" | "TVR":
                                content["instructor_annotation"]["value"] = "IDM"
                            case "CP":
                                content["instructor_annotation"]["value"] = "AD"
                            case _:
                                print("########## Annotation inattendue :", value)
                                continue
                        print("===(dict+str)===>", content["instructor_annotation"])
                else:
                    continue
            else:
                continue
            fraud_models.BeneficiaryFraudCheck.query.filter(
                fraud_models.BeneficiaryFraudCheck.id == fraud_check.id
            ).update({"resultContent": content}, synchronize_session=False)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--max-id", type=int, default=25_400_000)
    parser.add_argument("--min-id", type=int, default=-1)
    args = parser.parse_args()

    chunk_size = 200_000

    for chunk_start_id in range(args.max_id - chunk_size, args.min_id, -chunk_size):
        process(chunk_start_id, chunk_start_id + chunk_size)

        if args.not_dry:
            db.session.commit()
        else:
            db.session.rollback()

        # Ensure that script is not killed in production environment because of memory usage.
        db.session.expunge_all()
