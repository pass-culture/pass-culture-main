-- 3 indexes were recreated manually last week without UNIQUE, which is not consistent with the model.
SET lock_timeout='10s';
DROP INDEX "ix_special_event_externalId";
CREATE UNIQUE INDEX "ix_special_event_externalId" ON special_event ("externalId");
DROP INDEX "ix_special_event_question_externalId";
CREATE UNIQUE INDEX "ix_special_event_question_externalId" ON special_event_question ("externalId");
DROP INDEX "ix_special_event_response_externalId";
CREATE UNIQUE INDEX "ix_special_event_response_externalId" ON special_event_response ("externalId");
SET lock_timeout=0;
