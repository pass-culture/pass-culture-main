BACKUP_PATH=/data/backup_data
psql -d pass_culture -U pass_culture -f /data/clean_database.sql
#echo "Database cleaned"

echo $(date)
psql -d pass_culture -U pass_culture -f /data/backup_data/pre-data.sql
echo "restore pre-data"
psql -d pass_culture -U pass_culture -c "COPY recommendation FROM '/data/backup_data/recommendation.csv';"
echo "restore recommendations"
pg_restore -d pass_culture -U pass_culture -v /data/backup_data/data.pgdump
echo "restore data"
psql -d pass_culture -U pass_culture -f /data/backup_data/post-data.sql
echo "restore post-data"

#psql -Atx "postgres://pass_culture_9376:Nn9S9QPfY7RHk2Mdmq8C@127.0.0.1:10000/pass_culture_9376?sslmode=prefer"


# ALTER TABLE ONLY booking ADD CONSTRAINT "booking_recommendationId_fkey" FOREIGN KEY ("recommendationId") REFERENCES recommendation(id);